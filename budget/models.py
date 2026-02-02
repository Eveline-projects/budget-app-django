from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Q
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    TYPE_ACCOUNT = [
        ('ADULT', 'Adult'),
        ('CHILD', 'Child'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name_account = models.CharField(max_length=50)
    account_type = models.CharField(
        max_length=10,
        choices=TYPE_ACCOUNT,
        default='ADULT'
    )
    account_creation_date = models.DateTimeField(
        default=timezone.now
    )
    initial_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='The opening balance cannot be negative.')]
    )

    @property
    def total_balance(self):
        agg = self.transactions.aggregate(
            incomes=Sum('amount', filter=Q(type='IN')),
            outcomes=Sum('amount', filter=Q(type='OUT')),
        )
        return (agg['incomes'] or 0) - (agg['outcomes'] or 0)

    def __str__(self):
        return f"{self.name_account} - Balance: {self.total_balance}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Income'),
        ('OUT', 'Outcome'),
    ]
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='The amount must be greater than zero.')]
    )
    type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        default='OUT'
    )
    date = models.DateTimeField(
        default=timezone.now
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} PLN ({self.category.name if self.category else 'No Category'})"


class SavingsAccount(models.Model):
    TYPE_SAVE = [
        ('LOKATY', 'LOKATY'),
        ('FUNDUSZE', 'FUNDUSZE'),
        ('EMERYTURA', 'EMERYTURA'),
        ('INNE', 'INNE'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    saving_name = models.CharField(max_length=50)
    saving_type = models.CharField(max_length=10, choices=TYPE_SAVE, default='LOKATY')
    saving_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest_rate = models.FloatField(default=0.01)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user}: {self.saving_name} ({self.saving_type})"

    def get_absolute_url(self):
        if not self.pk:
            raise ValueError("Cannot reverse saving_detail because object has no PK yet")
        return reverse("budget:saving_detail", kwargs={"pk": self.pk})
