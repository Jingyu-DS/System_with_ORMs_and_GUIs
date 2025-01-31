
from account import SavingAccount, CheckingAccount

class Bank:
    """
    The Bank Class is composed by Saving Account and Checking Account, realizing the functions like open account, 
    summarize the accounts, select account, add transactions, list previous transtions and calculate interests and fees
    """

    def __init__(self):
        self.accounts = []
        self.current_account = None
        self.next_account_number = 1
    

    def menu(self) -> str:
        """This is the main menu when a user uses the bank system"""
        return f"""--------------------------------
Currently selected account: {self.current_account.display() if self.current_account else "None"}
Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit"""

    def open_account(self) -> None:
        """
        This function takes the input from users when users intend to open a new account in the bank. There are two account categories:
        Checking and Savings. 
        """
        account_type = input("Type of account? (checking/savings)\n>").strip().lower()
        if account_type == "savings":
            new_account = SavingAccount(account_type, self.next_account_number)
        if account_type == "checking":
            new_account = CheckingAccount(account_type, self.next_account_number)
        self.accounts.append(new_account)
        # print(self.accounts)
        self.next_account_number += 1
        # print("Account created successfully!")
        return None

    def summary(self):
        """
        This function is to provide a summary of accounts the bank is currently having
        """
        for account in self.accounts:
            print(account.display())

    def select_account(self) -> None:
        """
        When user selects a specific account, the function updates the current account to the newly selected account
        """
        account_number = int(input("Enter account number\n>"))
        account_number = f"{account_number:09d}"
        for account in self.accounts:
            if account.account_number == account_number:
                self.current_account = account
        return None
    
    def add_transaction(self) -> None:
        """
        The function is to take the transactions that the user intends the make. The transaction is composed by the amount and date
        """
        amount = float(input("Amount?\n>"))
        date = input("Date? (YYYY-MM-DD)\n>").strip()
        if self.current_account:
            self.current_account.add_transaction(amount, date)
        # else:
        #     print("Please select an account before adding transaction!")
        
        return None
    
    def list_transactions(self) -> None:
        """
        This function is to list all the past transations have been made from past to the latest
        """
        if self.current_account:
            print(self.current_account.list_transactions())
        # else:
        #     print("Please select an account first!")
        return None
    
    def interests_and_fees(self) -> None:
        """
        This function is calculate the interest and fee required for the current account
        """
        if self.current_account:
            self.current_account.interests_and_fees()
        # else:
        #     print("Please select an account first!")

        return None



