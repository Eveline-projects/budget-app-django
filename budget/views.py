from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse, reverse_lazy
from django.db.models import Sum
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    FormView,
    View
)

from .models import (
    Transaction,
    Category,
    BankAccount,
    SavingsAccount
)
from .forms import (
    RegisterForm,
    BankAccountForm,
    BankAccountCreateForm,
    SavingAccountForm,
    TransactionForm
)
import json

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'budget/register.html'
    success_url = reverse_lazy('budget:expense')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        default_categories = [
            'Food',
            'Bills',
            'Transport',
            'Entertainment',
            'Shopping',
            'Life',
            'Investments',
            'Other',
        ]
        for name in default_categories:
            Category.objects.get_or_create(
                user=self.object,
                name=name
            )

        return response


class ExpenseListView(LoginRequiredMixin, ListView):
    template_name = 'budget/expense.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_transactions = Transaction.objects.filter(user=self.request.user)
        total_in = user_transactions.filter(type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
        total_out = user_transactions.filter(type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0

        total_balance = total_in - total_out
        context['categories'] = Category.objects.filter(user=self.request.user)
        context['total_expenses'] = total_out
        context['total_balance'] = total_balance
        context['transaction_count'] = BankAccount.objects.filter(user=self.request.user).count()

        context['savings_count'] = SavingsAccount.objects.filter(user=self.request.user).count()
        context['total_savings'] = SavingsAccount.objects.filter(user=self.request.user).aggregate(
            total_sum=Sum('saving_balance')
        )['total_sum'] or 0

        return context


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = 'budget/account.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BankAccountCreateForm(user=self.request.user)
        return context


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountCreateForm
    template_name = 'budget/account.html'
    success_url = reverse_lazy('budget:account')

    def form_valid(self, form):
        form.instance.user = self.request.user
        account = form.save()
        amount = form.cleaned_data.get('initial_balance')
        category = form.cleaned_data.get('category')

        if amount and amount > 0:
            if not category:
                category, _ = Category.objects.get_or_create(
                    name="Other",
                    user=self.request.user
                )

            Transaction.objects.create(
                user=self.request.user,
                amount=amount,
                type='IN',
                category=category,
                account=account,
                description="Starting balance"
            )
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = BankAccount.objects.filter(user=self.request.user)
        return context


class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'budget/account_update.html'
    success_url = reverse_lazy('budget:account')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    model = BankAccount
    success_url = reverse_lazy('budget:account')

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'budget/login.html'
    success_url = reverse_lazy('budget:expense')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'budget/expense_create.html'
    success_url = reverse_lazy('budget:expense')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('budget:expense')


class ExpenseDetailView(DetailView):
    model = Transaction
    template_name = 'budget/expense_detail.html'
    context_object_name = 'expense'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'budget/category_create.html'
    success_url = reverse_lazy('budget:expense')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SavingCreateView(LoginRequiredMixin, CreateView):
    model = SavingsAccount
    form_class = SavingAccountForm
    template_name = 'budget/saving_add.html'


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['savings'] = SavingsAccount.objects.filter(user=self.request.user).order_by('-id')
        return context

class SavingDetailView(LoginRequiredMixin, DetailView):
    model = SavingsAccount
    template_name = 'budget/saving_detail.html'
    context_object_name = 'saving_detail'


class SavingListView(LoginRequiredMixin, ListView):
    model = SavingsAccount
    template_name = 'budget/saving_list.html'
    context_object_name = 'savings'

    def get_queryset(self):
        # Wszystkie oszczędności użytkownika, najnowsze najpierw
        return SavingsAccount.objects.filter(user=self.request.user).order_by('-id')


class StatisticsListView(ListView):
    template_name = 'budget/statistics.html'
    def get_queryset(self):
        data_query = Transaction.objects.filter(user=self.request.user).annotate(total=Sum('amount'))

        return data_query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_query = self.object_list.values('category__name', 'total')
        labels = [item['category__name'] for item in data_query if item['category__name']]
        values = [float(item['total']) for item in data_query]

        context['labels'] = json.dumps([labels])
        context['values'] = json.dumps(values)

        return context





