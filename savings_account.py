from decimal import Decimal
from account import Account
from datetime import datetime
import calendar
from utils import get_last_day_of_month
from transactions import Transaction
from exceptions import OverdrawError, TransactionLimitError, TransactionSequenceError
import logging
from sqlalchemy import Integer, ForeignKey, Float
from sqlalchemy.orm import mapped_column, Session
# from bank import Base


class SavingAccount(Account):
    """This SavingAccount class is a child class of Account class. It inherits some functions from the parent class but also realized
    some functions that are specific for saving account, including the upper limits for transaction frequency"""
    
    __tablename__ = "savings_account"

    account_id = mapped_column(Integer, ForeignKey("account.account_id"), primary_key = True)
    daily_limit = mapped_column(Integer, default = 2)
    monthly_limit = mapped_column(Integer, default = 5)
    interest_rate = mapped_column(Float, default = 0.33 / 100)
    __mapper_args__ = {"polymorphic_identity": "savings"}
    

    def __init__(self, account_type = "savings", *args, **kwargs):
        """Initiate the attributes specific to Saving Account"""
        super().__init__(account_type, *args, **kwargs)
    
    
    def add_transaction(self, session: Session, amount: float, date: str) -> bool:
        """This function is used to add transaction to saving account, subject to daily and monthly transaction frequency limits"""
        trans_date = datetime.strptime(date, "%Y-%m-%d")
        # daily = trans_date.date()
        year, month = trans_date.year, trans_date.month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])
        recent_transaction_date = self.latest_transaction_date(session)
        if recent_transaction_date and date < recent_transaction_date:
            raise TransactionSequenceError(recent_transaction_date)

        if self.get_balance(session) + Decimal(amount) < 0:
            raise OverdrawError("This transaction could not be completed due to an insufficient account balance.")
        
        daily_count = (session.query(Transaction).filter(
            Transaction.account_id == self.account_id,
            Transaction.date == date).count()
            )

        monthly_count = (session.query(Transaction).filter(
            Transaction.account_id == self.account_id,
            Transaction.date >= first_day,
            Transaction.date <= last_day)
        .count())

        if daily_count == self.daily_limit:
            raise TransactionLimitError("day", self.daily_limit)
        if monthly_count == self.monthly_limit:
            raise TransactionLimitError("month", self.monthly_limit)
        
        new_transaction = Transaction(session, date = date, amount = amount, account_id = self.account_id, \
                                      transaction_type = "Common")
        session.add(new_transaction)
        self.balance += amount
        session.commit()
        return True


    def interests_and_fees(self, session: Session) -> None:
        """This function is called and the interests will be calculated based on the balance on the current account"""
        latest_transaction_date = self.latest_transaction_date(session)
        interests_date = get_last_day_of_month(latest_transaction_date)
        latest_interest_date = self.latest_transaction_date(session, "Interests")
        if latest_interest_date and interests_date <= latest_interest_date:
            cur_month = datetime.strptime(interests_date, "%Y-%m-%d").strftime("%B")
            raise TransactionSequenceError(cur_month)

        amount = self.get_balance(session) * Decimal(self.interest_rate)
        interests = Transaction(session, date = interests_date, amount = float(amount), \
                                account_id = self.account_id, transaction_type = "Interests")
        session.add(interests)
        self.balance += float(amount)
        session.commit()
        logging.debug(f"Created transaction: {self.account_number}, {float(amount)}")
        self.latest_interest_date = interests_date
        return None


    def get_current_interest_rate(self) -> float:
        """This function is to get the interest rate if needed"""
        return self.interest_rate
    

    def reset_interest_rate(self, session: Session, r: float) -> None:
        """This function is to reset the interest rate if needed"""
        self.interest_rate = r
        session.commit()
        logging.debug("Saved to bank.db")
    

    def get_current_daily_trans_limits(self) -> int:
        """This function is to get the current daily upper limit of transaction frequency"""
        return self.daily_limit
    
    def reset_daily_trans_limits(self, session: Session, freq: int) -> None:
        """This function is to reset the current daily upper limit of transaction frequency if needed"""
        self.daily_limit = freq
        session.commit()
        logging.debug("Saved to bank.db")
    
    def get_current_monthly_trans_limits(self) -> int:
        """This function is to get the current monthly upper limit of transaction frequency"""
        return self.monthly_limit
    
    def reset_monthly_trans_limits(self, session: Session, freq: int) -> None:
        """This function is to reset the current monthly upper limit of transaction frequency if needed"""
        self.monthly_limit = freq
        session.commit()
        logging.debug("Saved to bank.db")


