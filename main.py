import hashlib
import json
import os
from typing import Dict, Optional
from decimal import Decimal
from account.account_user.users import User, UserType
from bank_accounts import BankAccount
from expenses import Expense, Category
import datetime

DATA_FILE = 'account/account_data/data/budget_data.json'


def default_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, (User, BankAccount, Expense)):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('__')}
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, (UserType, Category)):
        return obj.value

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


class Interface:
    def __init__(self):
        self.all_users: Dict[int, User] = {}
        self.all_bank_accounts: Dict[int, BankAccount] = {}
        self.all_expenses: Dict[int, Expense] = {}

        self.next_user_id = 1
        self.next_account_id = 1
        self.next_expense_id = 1

        self.current_user_id: Optional[int] = None

        self.load_data()


    def load_data(self):
        if not os.path.exists(DATA_FILE):
            print(f"INFO: Data file '{DATA_FILE}' doesn't exist. Starting with empty database.")
            return

        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            for user_data in data.get('users', []):
                user_type = UserType(user_data['user_type'])

                user = User(
                    username="temp",
                    user_type=user_type,
                    user_id=user_data['user_id']
                )

                user._username = user_data['_username']

                user.set_password_hash(user_data['_password_hash'])

                user.assigned_account = [int(aid) for aid in user_data['assigned_account']]  # KLUCZOWE
                user.assigned_expense = [int(eid) for eid in user_data['assigned_expense']]

                self.all_users[user.user_id] = user
                self.next_user_id = max(self.next_user_id, user.user_id + 1)

            for account_data in data.get('bank_accounts', []):
                account = BankAccount(
                    account_id=account_data['account_id'],
                    user_id=account_data['user_id'],
                    account_type=account_data['account_type'],
                    initial_balance=Decimal(account_data['balance'])
                )
                self.all_bank_accounts[account.account_id] = account
                self.next_account_id = max(self.next_account_id, account.account_id + 1)

            for expense_data in data.get('expenses', []):
                expense_id = expense_data['_expense_id']

                expense = Expense(
                    amount=Decimal(expense_data['amount']),
                    category=Category(expense_data['category']),
                    account_id=expense_data['account_id'],
                    expense_id=expense_id,
                    description=expense_data['description']
                )
                self.all_expenses[expense.expense_id] = expense
                self.next_expense_id = max(self.next_expense_id, expense.expense_id + 1)

            self.current_user_id = data.get('current_user_id')

            print(f"Data loaded successfully {DATA_FILE}. Found: {len(self.all_users)} users.")

        except Exception as e:
            print(f"Can't load JSON data: {e}")


    def save_data(self):
        data_to_save = {
            'users': list(self.all_users.values()),
            'bank_accounts': list(self.all_bank_accounts.values()),
            'expenses': list(self.all_expenses.values()),
            'current_user_id': self.current_user_id,
            'next_user_id': self.next_user_id,
            'next_account_id': self.next_account_id,
            'next_expense_id': self.next_expense_id,
        }
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4, default=default_serializer)
            print(f"\nData saved successfully to {DATA_FILE}.")
        except Exception as e:
            print(f"Can't load JSON data: {e}")


    def get_current_user(self) -> User | None:
        if self.current_user_id is None:
            return None
        return self.all_users.get(self.current_user_id)


    def find_user_by_username(self, username: str) -> User | None:
        for user in self.all_users.values():
            if user.username.lower() == username.lower():
                return user
        return None


    def create_new_user_interface(self):
        print("\n--- USER REGISTRATION ---")
        while True:
            username = input("Enter new username: ").strip()
            if self.find_user_by_username(username):
                print("Username taken.")
                continue
            try:
                temp_user = User(username='DUMMY', user_type=UserType.ADULT, user_id=0)
                temp_user.username = username
                break
            except ValueError as e:
                print(f"{e}")
        while True:
            password = input("New password (at least 6 characters): ")
            if len(password) < 6:
                print("Password is too short.")
                continue
            if password != input("Confirm password: "):
                print("Passwords are not the same.")
                continue
            break

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user_type = UserType.ADULT

        new_user = User(
            user_id=self.next_user_id,
            username=username,
            user_type=user_type
        )
        new_user.set_password_hash(password_hash)

        self.all_users[self.next_user_id] = new_user
        self.next_user_id += 1
        self.current_user_id = new_user.user_id

        print(f"\nCreated and logged in as {username.upper()}.")


    def login_interface(self):
        print("\n--- SIGN IN ---")
        username = input("Username: ").strip()
        password = input("Password: ")

        user = self.find_user_by_username(username)

        if user is None:
            print("Incorrect username or password")
            return

        input_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if user.verify_password(input_hash):
            self.current_user_id = user.user_id
            print(f"Singed in! Welcome, {user.username}.")
        else:
            print("Incorrect username or password")


    def add_existing_account_interface(self):
        current_user = self.get_current_user()
        if current_user is None:
            print("You have to be signed in to add an account.")
            return

        print("\n--- CREATING NEW ACCOUNT (Test) ---")
        while True:
            account_type = input("Enter account type (ADMIN, CHILD, ADULT): ")
            if account_type.lower() in ('admin', 'child', 'adult'):
                account_type = account_type.upper()
                print(f'Assigned type {account_type.upper()}')
                break
            else:
                print('invalid input')

        try:
            initial_balance = Decimal(input("Enter starting amount (e.g. 100.00): "))
        except ValueError:
            print("Incorrect format")
            return

        new_account = BankAccount(
            account_id=self.next_account_id,
            user_id=current_user.user_id,
            account_type=account_type,
            initial_balance=initial_balance
        )
        self.all_bank_accounts[self.next_account_id] = new_account
        self.next_account_id += 1

        success, message = current_user.add_account(new_account)

        if success:
            print(f"SUCCESS: {message}")
        else:
            print(f"ERROR: {message}")


    def view_financial_overview_interface(self):
        current_user = self.get_current_user()
        if current_user is None:
            print("Not logged in.")
            return

        print("\n" + "=" * 50)
        print(f"FINANCES REVIEW for {current_user.username.upper()}")
        print("=" * 50)

        total_balance = Decimal('0.00')
        account_ids = current_user.assigned_account

        if not account_ids:
            print("No assigned accounts.")

        for account_id in account_ids:
            account = self.all_bank_accounts.get(account_id)

            if account:
                print(f"  - ID {account.account_id}: {account.account_type} | amount: ${account.balance:.2f}")
                total_balance += account.balance

        print("-" * 50)
        print(f"TOTAL BALANCE: ${total_balance:.2f}")
        print("=" * 50)


    def add_new_expense_interface(self):
        curr_user = self.get_current_user()
        if curr_user is None:
            print("Not logged in.")
            return

        available_accs = {
            acc_id: self.all_bank_accounts[acc_id]
            for acc_id in curr_user.assigned_account
            if acc_id in self.all_bank_accounts
        }

        if not available_accs:
            print("No available accounts. Add an account (6)")
            return

        print('Available accounts: ')
        for acc in available_accs.values():
            print(f"- {acc.account_id}: {acc.account_type} --- Balance: {acc.balance:.2f}")

        selected_acc = None
        while selected_acc is None:
            try:
                acc_id_input = int(input("Select an account ID: "))
                if acc_id_input in available_accs:
                    selected_acc = available_accs[acc_id_input]
                    break
                else:
                    print("Invalid ID")
            except ValueError:
                print("Invalid ID")

        try:
            amount = Decimal(input("Enter new expense amount: "))
            if amount <= 0:
                print("Invalid amount.")
                return
        except ValueError:
            print("Incorrect format. (e.g. 123.45)")
            return

        cat_list = [c.value.upper() for c in Category]
        print(f'Categories: {", ".join(cat_list)}')

        category = None
        while category is None:
            cat_input = input("Enter a category (e.g. FOOD): ")
            try:
                category = Category(cat_input)
            except ValueError:
                print("Invalid category.")

        desc = input("Enter a description of your expense: ").strip()


        if selected_acc.withdraw(amount): #true jesli wystarczajace saldo
            new_id = self.next_expense_id
            self.next_expense_id += 1

            new_expense = Expense(
                amount=amount,
                category=category,
                account_id=selected_acc.account_id,
                expense_id=new_id,
                description=desc,
            )

            expense_id_str = int(new_expense.expense_id) # pobieranie uuid jako str
            self.all_expenses[new_id] = new_expense
            curr_user.add_expense(new_id)

            selected_acc.add_expense_id(new_id)

            print(f"EXPENSE {new_expense.category.value.capitalize()}: {new_expense.amount:.2f}")
        else:
            print("Transaction cancelled.")


    def show_user_expenses_interface(self):
        current_user = self.get_current_user()
        if current_user is None:
            print("You have to be signed in.")
            return

        expense_ids = current_user.assigned_expense

        if not expense_ids:
            print(f"\nUser {current_user.username} haven't added any expenses.")
            return

        print(f"\n--- EXPENSES FOR {current_user.username.upper()} ---")

        for expense_id in expense_ids:
            expense = self.all_expenses.get(expense_id)

            if expense:
                account = self.all_bank_accounts.get(expense.account_id)
                account_type = account.account_type if account else "Unknown Account"
                print(
                    f"ID: {expense.expense_id} | Amount: ${expense.amount:.2f} | Category: {expense.category.value} | Paid with: {account_type}")
                if expense.description:
                    print(f"    Description: {expense.description}")
        print("---------------------------------------")


    def display_main_menu(self):
        print("\n" + "=" * 30)
        print("         HOME BUDGET")
        print("=" * 30)
        if self.current_user_id is None:
            print("1. Sign in")
            print("2. Register (New account)")
            print("0. Quit")
        else:
            print(f"Logged as: {self.get_current_user().username}")
            print("3. Finance Overview")
            print("4. Add New Expense")
            print("5. Expense History")
            print("6. New Bank Account")
            print("7. Log Out")
            print("0. Save and Quit")


    def run(self):
        while True:
            self.display_main_menu()
            choice = input("Choose Option: ").strip()

            if choice == '0':
                self.save_data()
                print("See You!")
                break

            if self.current_user_id is None:
                if choice == '1':
                    self.login_interface()
                elif choice == '2':
                    self.create_new_user_interface()
                else:
                    print("\nIncorrect choice.")
            else:
                if choice == '3':
                    self.view_financial_overview_interface()
                elif choice == '4':
                    self.add_new_expense_interface()
                elif choice == '5':
                    self.show_user_expenses_interface()
                elif choice == '6':
                    self.add_existing_account_interface()
                elif choice == '7':
                    self.current_user_id = None; print("Logged Out.")
                else:
                    print("\nIncorrect choice.")

if __name__ == "__main__":
    app = Interface()
    app.run()

