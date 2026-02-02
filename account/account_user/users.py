from enum import auto, StrEnum
from bank_accounts import BankAccount
from typing import List, Tuple, Dict


class UserType(StrEnum):
    ADMIN = auto()
    ADULT = auto()
    CHILD = auto()


class User:
    def __init__(self, username: str, user_type: UserType, user_id: int):
        self._username = ""
        self.username = username
        self.user_type = user_type
        self.user_id = user_id

        self.assigned_account: List[int] = []
        self.assigned_expense: Dict[int,bool] = {}

        self._password_hash = ""

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username: str):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username cannot be empty")
        self._username = username.strip()

    def set_password_hash(self, password_hash):
        self._password_hash = password_hash

    def verify_password(self, password_hash):
        return self._password_hash == password_hash

    def add_account(self, account: BankAccount) -> Tuple[bool, str]:
        if account.user_id != self.user_id:
            return (False,
                f"Error: Account ID: {account.account_id} is for User ID {account.user_id}, not {self.username}.")

        account_id = account.account_id

        if account_id in self.assigned_account:
            return False, f"Account ID {account_id} is already assigned to this user."

        self.assigned_account.append(account_id)
        return True, f"Account '{account.account_type}' (ID: {account.account_id}) added successfully."

    def add_expense(self, expense: int) -> bool:
        if expense in self.assigned_expense:
            return False
        self.assigned_expense[expense] = True
        return True

    def get_assigned_account(self) -> List[int]:
        return self.assigned_account

    def get_assigned_expense(self) -> List[int]:
        return list(self.assigned_expense.keys())

    def __str__(self):
        return (f"User ID: {self.user_id}, Username: {self.username}, Type: {self.user_type.value.capitalize()}\n"
                f"  Accounts IDs: {self.assigned_account}\n"
                f"  Expenses IDs Count: {len(self.assigned_expense)}")

