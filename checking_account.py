
from decimal import Decimal, ROUND_HALF_UP
from account import Account
from datetime import datetime
from utils import get_last_day_of_month
from transactions import Transaction
from excpetions import OverdrawError, TransactionSequenceError
import logging


class CheckingAccount(Account):
    """This CheckingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for checking account, including the upper limits for transaction frequency"""

    def __init__(self, account_type: str, account_number: int, latest_interest_date = None, *args, **kwargs):
        """Initiate the attributes specific to Checking Account"""
        super().__init__(account_type, account_number, latest_interest_date, *args, **kwargs)
        self.__interest_rate = 0.08 / 100
        self.__low_balance = 100
        self.__low_threshold_fee = -5.75
    
    def add_transaction(self, amount: float, date: str) -> bool:
        """This function is used to add transaction to saving account, no frequency limits"""
        # trans_date = datetime.strptime(date, "%Y-%m-%d")
        recent_transaction_date = self.latest_transaction_date()
        if recent_transaction_date is not None and date < recent_transaction_date:
            raise TransactionSequenceError(recent_transaction_date)

        if self.get_balance() + Decimal(amount) < 0:
            raise OverdrawError("This transaction could not be completed due to an insufficient account balance.")
        self.transactions.append(Transaction(date, amount))
        return True
    
    def interests_and_fees(self) -> None:
        """This function is called and the interests and low balance fee will be calculated based on the balance on the current account"""
        latest_transaction = self.latest_transaction_date()
        interests_date = get_last_day_of_month(latest_transaction)
        if self.latest_interest_date and interests_date <= self.latest_interest_date:
            cur_month = datetime.strptime(interests_date, "%Y-%m-%d").strftime("%B")
            raise TransactionSequenceError(cur_month)
        
        interests = self.get_balance() * Decimal(self.__interest_rate)
        self.transactions.append(Transaction(interests_date, interests))
        logging.debug(f"Created transaction: {self.account_num}, {float(interests)}")
        self.latest_interest_date = interests_date

        if self.get_balance() <= self.__low_balance:
            self.transactions.append(Transaction(interests_date, self.__low_threshold_fee))
            logging.debug(f"Created transaction: {self.account_num}, {self.__low_threshold_fee}")
        return None
    
    
    def get_current_interest_rate(self) -> float:
        """This function is to get the interest rate if needed"""
        return self.__interest_rate


    def get_current_low_balance_fee(self) -> float:
        """This function is to get the low balance fee if needed"""
        return self.__low_threshold_fee
    
    def get_current_low_balance(self) -> int:
        """This function is to get the low balance if needed"""
        return self.__low_balance

    def reset_interest_rate(self, r: float) -> None:
        """This function is to reset the interest rate if needed"""
        self.__interest_rate = r
        return None
    
    def reset_interest_rate(self, f: int) -> None:
        """This function is to reset the low balance if needed"""
        self.__low_balance = f
        return None
    

    def reset_low_balance_fee(self, f: float) -> None:
        """This function is to reset the low balance fee if needed"""
        self.__low_threshold_fee = f
        return None
