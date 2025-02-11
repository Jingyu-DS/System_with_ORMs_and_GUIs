
from decimal import Decimal, ROUND_HALF_UP
import collections
from account import Account
from datetime import datetime
from utils import get_last_day_of_month
from excpetions import OverdrawError, TransactionSequenceError


class CheckingAccount(Account):
    """This CheckingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for checking account, including the upper limits for transaction frequency"""

    def __init__(self, account_type: str, account_number: int, latest_transaction_date = None, latest_interest_date = None, *args, **kwargs):
        """Initiate the attributes specific to Checking Account"""
        super().__init__(account_type, account_number, latest_transaction_date, latest_interest_date, *args, **kwargs)
        self.__interest_rate = 0.08 / 100
        self.__low_threshold_fee = -5.75
    
    def add_transaction(self, amount: float, date: str) -> bool:
        """This function is used to add transaction to saving account, no frequency limits"""
        # trans_date = datetime.strptime(date, "%Y-%m-%d")
        if self.latest_transaction_date is not None and date < self.latest_transaction_date:
            raise TransactionSequenceError(self.latest_transaction_date)

        if self.get_balance() + Decimal(amount) < 0:
            raise OverdrawError("This transaction could not be completed due to an insufficient account balance.")
        self.latest_transaction_date = date
        self.transactions.append((date, len(self.transactions), Decimal(amount)))
        # print("Successful Transaction")
        return True
    
    def interests_and_fees(self) -> None:
        """This function is called and the interests and low balance fee will be calculated based on the balance on the current account"""
        self.transactions.sort()
        latest_transaction_date = self.transactions[-1][0]
        interests_date = get_last_day_of_month(latest_transaction_date)
        if self.latest_interest_date and interests_date <= self.latest_interest_date:
            cur_month = datetime.strptime(interests_date, "%Y-%m-%d").strftime("%B")
            raise TransactionSequenceError(cur_month)
        
        interests = self.get_balance() * Decimal(self.__interest_rate)
        self.transactions.append((interests_date, len(self.transactions), Decimal(interests)))
        self.latest_transaction_date = interests_date
        self.latest_interest_date = interests_date

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
