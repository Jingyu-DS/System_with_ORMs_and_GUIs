
from decimal import Decimal
from account import Account
from datetime import datetime
from utils import get_last_day_of_month
from transactions import Transaction
from excpetions import OverdrawError, TransactionSequenceError
import logging
from sqlalchemy import Integer, ForeignKey, Float
from sqlalchemy.orm import mapped_column, Session
# from bank import Base


class CheckingAccount(Account):
    """This CheckingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for checking account, including the upper limits for transaction frequency"""

    __tablename__ = "checking_account"
    account_id = mapped_column(Integer, ForeignKey("account.account_id"), primary_key = True)
    low_balance = mapped_column(Float, default = 100.0)
    low_threshold_fee = mapped_column(Float, default = -5.75)
    interest_rate = mapped_column(Float, default=0.08 / 100)

    __mapper_args__ = {"polymorphic_identity": "checking"}


    def __init__(self, account_type = "checking", latest_interest_date = None, *args, **kwargs):
        """Initiate the attributes specific to Checking Account"""
        super().__init__(account_type, latest_interest_date, *args, **kwargs)
    
    def add_transaction(self, session: Session, amount: float, date: str) -> bool:
        """This function is used to add transaction to saving account, no frequency limits"""
        # trans_date = datetime.strptime(date, "%Y-%m-%d")
        recent_transaction_date = self.latest_transaction_date(session)
        if recent_transaction_date is not None and date < recent_transaction_date:
            raise TransactionSequenceError(recent_transaction_date)

        if self.get_balance(session) + Decimal(amount) < 0:
            raise OverdrawError("This transaction could not be completed due to an insufficient account balance.")
        new_transaction = Transaction(session, date = date, amount = amount, account_id = self.account_id, transaction_type = "Common")
        session.add(new_transaction)
        self.balance += amount
        session.commit()
        return True
    
    def interests_and_fees(self, session: Session) -> None:
        """This function is called and the interests and low balance fee will be calculated based on the balance on the current account"""
        latest_transaction = self.latest_transaction_date(session)
        # print(latest_transaction)
        interests_date = get_last_day_of_month(latest_transaction)
        latest_interest_date = self.latest_transaction_date(session, "Interests")
        if latest_interest_date and interests_date <= latest_interest_date:
            cur_month = datetime.strptime(interests_date, "%Y-%m-%d").strftime("%B")
            raise TransactionSequenceError(cur_month)
        
        amount = self.get_balance(session) * Decimal(self.interest_rate)
        interests = Transaction(session, date = interests_date, amount = float(amount), \
                                account_id = self.account_id, transaction_type = "Interests")
        session.add(interests)
        self.balance += float(amount)
        logging.debug(f"Created transaction: {self.account_number}, {float(amount)}")
        # self.latest_interest_date = interests_date

        if self.get_balance(session) <= self.low_balance:
            fees = Transaction(session, date = interests_date, amount = self.low_threshold_fee,\
                                account_id = self.account_id, transaction_type = "LowBalance")
            session.add(fees)
            self.balance += self.low_threshold_fee
            logging.debug(f"Created transaction: {self.account_number}, {self.low_threshold_fee}")
        
        session.commit()
        return None
    
    
    def get_current_interest_rate(self) -> float:
        """This function is to get the interest rate if needed"""
        return self.interest_rate


    def get_current_low_balance_fee(self) -> float:
        """This function is to get the low balance fee if needed"""
        return self.low_threshold_fee
    
    def get_current_low_balance(self) -> int:
        """This function is to get the low balance if needed"""
        return self.low_balance

    def reset_interest_rate(self, session: Session, rate: float) -> None:
        """Resets the interest rate."""
        self.interest_rate = rate
        session.commit()

    def reset_low_balance(self, session: Session, balance: float) -> None:
        """Resets the low balance threshold."""
        self.low_balance = balance
        session.commit()

    def reset_low_balance_fee(self, session: Session, fee: float) -> None:
        """Resets the low balance fee."""
        self.low_threshold_fee = fee
        session.commit()
