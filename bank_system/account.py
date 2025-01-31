from decimal import Decimal, ROUND_HALF_UP
import collections
from datetime import datetime
from utils import get_last_day_of_month

class Account:
    """The Account Class is used as a parent class for both Checking and Saving Accouts to realize several fundemantal functions
    Including the get balance, list transactions, display the current information for the account. Adding transactions and getting
    interests and fees functions are different between checking and saving accounts. Thus, they will be realized in the child classes"""
    
    def __init__(self, account_type: str, account_number: int):
        """Initiate the account with the corresponding account number and the required account type"""
        self.account_type = account_type
        self.account_number = f"{account_number:09d}"
        # tansactions are saved as tuple (date, trans_times,transaction amount)
        self.transactions = []

    def get_balance(self):
        """This function is used to get the current balance of the selected account. If there have been no transactions yet, 
        the else condition is used to handle the empty transaction records"""
        if self.transactions:
            total = sum(transaction[2] for transaction in self.transactions)
        else:
            total = Decimal(0.00)
        return total

    def display(self) -> str:
        """Use to show the information including account type, account number and current balance of the selected account"""
        current_total = self.get_balance().quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{self.account_type[0].upper() + self.account_type[1:]}#{self.account_number},\tbalance: ${current_total:,.2f}"


    def list_transactions(self) -> str:
        """Return the transactions from the earliest to latest in the format as required"""
        self.transactions.sort()
        transations = ""
        for i in range(len(self.transactions)):
            date, _, amount = self.transactions[i]
            cur = f"{date}, ${amount:,.2f}"
            transations += cur
            if i < len(self.transactions) - 1:
                transations += "\n"
        return transations
                
            

class SavingAccount(Account):
    """This SavingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for saving account, including the upper limits for transaction frequency"""
    
    def __init__(self, account_type: str, account_number: int, *args, **kwargs):
        """Initiate the attributes specific to Saving Account"""
        super().__init__(account_type, account_number, *args, **kwargs)
        self.daily_transaction = collections.defaultdict(int)
        self.monthly_transaction = collections.defaultdict(int)
        self.__daily_limit = 2
        self.__monthly_limit = 5
        self.__interest_rate = 0.33 / 100
    
    def add_transaction(self, amount: float, date: str) -> bool:
        """This function is used to add transaction to saving account, subject to daily and monthly transaction frequency limits"""
        trans_date = datetime.strptime(date, "%Y-%m-%d")
        daily = trans_date.date()
        monthly = trans_date.strftime("%Y-%m")

        if self.get_balance() + Decimal(amount) < 0:
            # print("Unsuccessful Transaction: Insufficient Account Balance")
            return False

        if self.daily_transaction[daily] == self.__daily_limit:
            # print("Unsuccessful Transaction: Maximum Daily Transactions have been achieved")
            return False
        
        if self.monthly_transaction[monthly] == self.__monthly_limit:
            # print("Unsuccessful Transaction: Maximum Monthly Transactions have been achieved")
            return False
        
        self.transactions.append((date, len(self.transactions), Decimal(amount)))
        self.daily_transaction[daily] += 1
        self.monthly_transaction[monthly] += 1
        # print("Successful Transaction")
        return True


    def interests_and_fees(self) -> None:
        """This function is called and the interests will be calculated based on the balance on the current account"""
        self.transactions.sort() # sort will be based on the date and the order they entered
        latest_transaction_date = self.transactions[-1][0]
        interests_date = get_last_day_of_month(latest_transaction_date)
        interests = self.get_balance() * Decimal(self.__interest_rate)
        self.transactions.append((interests_date, len(self.transactions), Decimal(interests)))
        return None


    def get_current_interest_rate(self) -> float:
        """This function is to get the interest rate if needed"""
        return self.__interest_rate
    

    def reset_interest_rate(self, r: float) -> None:
        """This function is to reset the interest rate if needed"""
        self.__interest_rate = r
        return None
    

    def get_current_daily_trans_limits(self) -> int:
        """This function is to get the current daily upper limit of transaction frequency"""
        return self.__daily_limit
    
    def reset_daily_trans_limits(self, freq: int) -> None:
        """This function is to reset the current daily upper limit of transaction frequency if needed"""
        self.__daily_limit = freq
        return None
    
    def get_current_monthly_trans_limits(self) -> int:
        """This function is to get the current monthly upper limit of transaction frequency"""
        return self.__monthly_limit
    
    def reset_monthly_trans_limits(self, freq: int) -> None:
        """This function is to reset the current monthly upper limit of transaction frequency if needed"""
        self.__monthly_limit = freq
        return None



class CheckingAccount(Account):
    """This CheckingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for checking account, including the upper limits for transaction frequency"""

    def __init__(self, account_type: str, account_number: int, *args, **kwargs):
        """Initiate the attributes specific to Checking Account"""
        super().__init__(account_type, account_number, *args, **kwargs)
        self.__interest_rate = 0.08 / 100
        self.__low_threshold_fee = -5.75
    
    def add_transaction(self, amount: float, date: str) -> bool:
        """This function is used to add transaction to saving account, no frequency limits"""
        # trans_date = datetime.strptime(date, "%Y-%m-%d")
        if self.get_balance() + Decimal(amount) < 0:
            print("Unsuccessful Transaction: Insufficient Account Balance")
            return False
        self.transactions.append((date, len(self.transactions), Decimal(amount)))
        # print("Successful Transaction")
        return True
    
    def interests_and_fees(self) -> None:
        """This function is called and the interests and low balance fee will be calculated based on the balance on the current account"""
        self.transactions.sort()
        latest_transaction_date = self.transactions[-1][0]
        interests_date = get_last_day_of_month(latest_transaction_date)
        interests = self.get_balance() * Decimal(self.__interest_rate)
        self.transactions.append((interests_date, len(self.transactions), Decimal(interests)))

        if self.get_balance() <= 100:
            self.transactions.append((interests_date, len(self.transactions), Decimal(self.__low_threshold_fee)))
        
        return None
    
    def get_current_interest_rate(self) -> float:
        """This function is to get the interest rate if needed"""
        return self.__interest_rate


    def get_current_low_balance_fee(self) -> float:
        """This function is to get the low balance fee if needed"""
        return self.__low_threshold_fee

    def reset_interest_rate(self, r: float) -> None:
        """This function is to reset the interest rate if needed"""
        self.__interest_rate = r
        return None
    

    def reset_low_balance_fee(self, f: float) -> None:
        """This function is to reset the low balance fee if needed"""
        self.__low_threshold_fee = f
        return None
