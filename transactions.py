from decimal import Decimal
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import mapped_column, relationship
from bank import Base

class Transaction(Base):
    """This class is designed to indicate a transaction. It will handle the functions including
    the display of each transaction, decision related to how to sort the transactions in the account"""

    __tablename__ = "transactions"

    transaction_id = mapped_column(Integer, primary_key = True)
    account_id = mapped_column(Integer, ForeignKey("account.account_id"), nullable = False)
    amount = mapped_column(Float, nullable = False)
    date = mapped_column(String, nullable = False)
    transaction_type = mapped_column(String, nullable = False)
    account = relationship("Account", back_populates="transactions")


    def __init__(self, session, date: str, amount: float, account_id: int, transaction_type: str):
        """Initiate a transaction"""
        last_transaction = session.query(Transaction).order_by(Transaction.transaction_id.desc()).first()
        self.transaction_id =  last_transaction.transaction_id + 1
        self.date = date
        self.amount = amount
        self.account_id = account_id
        self.transaction_type = transaction_type
    
    def __str__(self) -> str:
        """Formats the date and amount of this transaction"""
        return f"{self.date}, ${Decimal(self.amount):,.2f}"

    def __lt__(self, other) -> bool:
        """This function is to ensure the order of sorting and getting the most recent transaction"""
        if self.date == other.date:
            return self.transaction_id < other.transaction_id
        return self.date < other.date
    

    def __radd__(self, other) -> Decimal:
        """Allows transactions to be summed by their amounts."""
        return other + Decimal(self.amount)
    




    

