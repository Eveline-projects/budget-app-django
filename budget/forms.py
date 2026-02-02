from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BankAccount, Category, SavingsAccount, Transaction


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']


class BankAccountForm(forms.ModelForm):
    initial_balance = forms.DecimalField(
        label="Starting balance",
        initial=0,
        min_value=0,
        required=False,
        help_text='Enter the current balance of this account.',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="First deposit category",
        required=False
    )

    class Meta:
        model = BankAccount
        fields = ['name_account', 'account_type', 'initial_balance', 'category']
        help_texts = {
            'name_account': 'For example, My savings, Main account.',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)


class BankAccountCreateForm(BankAccountForm):
    initial_balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Starting balance",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="First deposit category",
    )

    class Meta(BankAccountForm.Meta):
        fields = BankAccountForm.Meta.fields + ['initial_balance', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
        else:
            self.fields['category'].queryset = Category.objects.all()


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'category', 'account', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['account'].queryset = BankAccount.objects.filter(user=user)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SavingAccountForm(forms.ModelForm):
    class Meta:
        model = SavingsAccount
        fields = [
            'saving_name',
            'saving_type',
            'saving_balance',
            'interest_rate',
        ]
        labels = {
            'saving_name': 'Nazwa konta',
            'saving_type': 'Typ konta',
            'saving_balance': 'Saldo początkowe',
            'interest_rate': 'Oprocentowanie',
        }
        widgets = {
            'saving_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Np. Lokata PKO'
            }),
            'saving_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'saving_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
        }

    def clean_saving_balance(self):
        balance = self.cleaned_data['saving_balance']
        if balance < 0:
            raise forms.ValidationError("Saldo nie może być ujemne.")
        return balance