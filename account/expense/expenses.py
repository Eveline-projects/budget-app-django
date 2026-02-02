from datetime import datetime, date
from decimal import Decimal
from enum import StrEnum, auto
from typing import Optional

class Category(StrEnum):
    FOOD = auto()
    HOME = auto()
    TRANSPORT = auto()
    ENTERTAINMENT = auto()
    LIFE = auto()
    SHOPPING = auto()
    BILLS = auto()
    INVESTMENTS = auto()


class Expense:
    def __init__(self, amount, category, account_id, expense_id, description: Optional[str] = ''):
        self.category: Category = category
        self.account_id = account_id
        self.date: datetime = datetime.today()
        self._expense_id: int = expense_id
        self.amount: Decimal = Decimal(str(amount))
        self.description: Optional[str] = description


    def modify_expense(self):
        print(self.amount)
        print(self.category)
        print(self.account_id)
        while True:
            print('1. modify expense amount')
            print('2. modify expense category')
            print('3. modify to which account')
            print('4. quit')
            choice = input('which to modify: ')
            try:
                if choice == '1':
                    self.amount = Decimal(input('amount to modify: '))
                if choice == '2':
                    cat_choice = input('category to modify: ').lower()
                    self.category = Category(cat_choice)
                if choice == '3':
                    pass
                if choice == '4':
                    break
            except ValueError as e:
                print(e)


    def __str__(self):
        description_str = f" ({self.description})" if self.description else ""
        return (
            f"Expense ID: {self.expense_id} | Amount: ${self.amount:.2f} | "f"Category: {self.category.value.capitalize()}{description_str} | "f"Paid from Account ID: {self.account_id}")


    @property
    def expense_id(self):
        return self._expense_id
