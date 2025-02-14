from decimal import Decimal, ROUND_HALF_UP
import collections
from account import Account
from datetime import datetime
from utils import get_last_day_of_month
from transactions import Transaction
from excpetions import OverdrawError, TransactionLimitError, TransactionSequenceError
import logging


class SavingAccount(Account):
    """This SavingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for saving account, including the upper limits for transaction frequency"""
    
    def __init__(self, account_type: str, account_number: int, latest_interest_date = None, *args, **kwargs):
        """Initiate the attributes specific to Saving Account"""
        super().__init__(account_type, account_number, latest_interest_date, *args, **kwargs)
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
        recent_transaction_date = self.latest_transaction_date()

        if recent_transaction_date and date < recent_transaction_date:
            raise TransactionSequenceError(recent_transaction_date)

        if self.get_balance() + Decimal(amount) < 0:
            raise OverdrawError("This transaction could not be completed due to an insufficient account balance.")

        if self.daily_transaction[daily] == self.__daily_limit:
            raise TransactionLimitError("day", self.__daily_limit)
        
        if self.monthly_transaction[monthly] == self.__monthly_limit:
            raise TransactionLimitError("month", self.__monthly_limit)
        
        self.transactions.append(Transaction(date, amount))
        self.daily_transaction[daily] += 1
        self.monthly_transaction[monthly] += 1
        return True


    def interests_and_fees(self) -> None:
        """This function is called and the interests will be calculated based on the balance on the current account"""
        latest_transaction_date = self.latest_transaction_date()
        interests_date = get_last_day_of_month(latest_transaction_date)
        if self.latest_interest_date and interests_date <= self.latest_interest_date:
            cur_month = datetime.strptime(interests_date, "%Y-%m-%d").strftime("%B")
            raise TransactionSequenceError(cur_month)

        interests = self.get_balance() * Decimal(self.__interest_rate)
        self.transactions.append(Transaction(interests_date, interests))
        logging.debug(f"Created transaction: {self.account_num}, {float(interests)}")
        self.latest_interest_date = interests_date
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


