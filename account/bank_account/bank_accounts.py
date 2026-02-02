from datetime import datetime
from typing import List
from decimal import Decimal


class BankAccount:
    def __init__(self, account_id: int, user_id: int, account_type: str,
                 initial_balance: Decimal, is_active: bool = True ):
        self.account_id = account_id
        self.user_id = user_id
        self.account_type = account_type
        self.balance: Decimal = initial_balance
        self.is_active = is_active

        self.assigned_expense_ids: List[int] = []

        self._creation_date: datetime = datetime.today()


    def deposit(self, amount: Decimal) -> bool:
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        if self.is_active and amount > Decimal('0.00'):
            self.balance += amount
            print(f"Deposit of ${amount:.2f} successful. New balance: $ {self.balance:.2f}.")
            return True
        return False

    def withdraw(self, amount: Decimal) -> bool:
        if not isinstance(amount, Decimal):
            raise TypeError("Withdrawal amount must be Decimal.")

        if self.balance >= amount:
            self.balance -= amount
            return True
        return False


    def add_expense_id(self, expense_id: int) -> bool:
        if expense_id not in self.assigned_expense_ids:
            self.assigned_expense_ids.append(expense_id)
            print(f"Expense added to account")
            return True
        return False


    def get_creation_date(self) -> datetime:
        return self._creation_date


    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return (f"Account ID: {self.account_id}, Type: {self.account_type}({status})\n"
                f" Balance: {self.balance:.2f}, "
                f" Created: {self._creation_date}\n"
                f' Expenses Count: {len(self.assigned_expense_ids)}')


