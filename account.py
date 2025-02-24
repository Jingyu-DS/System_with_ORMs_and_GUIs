from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, Float, select
from sqlalchemy.orm import mapped_column, relationship, Session
from bank import Base
from transactions import Transaction

class Account(Base):
    """The Account Class is used as a parent class for both Checking and Saving Accouts to realize several fundemantal functions
    Including the get balance, list transactions, display the current information for the account. Adding transactions and getting
    interests and fees functions are different between checking and saving accounts. Thus, they will be realized in the child classes"""
    
    __tablename__ = "account"

    # account_id = mapped_column(Integer, primary_key = True, autoincrement = True)
    account_id = mapped_column(Integer, primary_key = True)  
    account_number = mapped_column(String, unique = True, nullable = False)
    account_type = mapped_column(String, nullable = False)
    balance = mapped_column(Float, default = 0.00)
    type = mapped_column(String, nullable = False)  
    bank_id = mapped_column(Integer, ForeignKey("bank._id"))
    bank = relationship("Bank", back_populates = "accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "account",
        "polymorphic_on": type,
    }

    
    def __init__(self, account_type: str, latest_interest_date = None):
        """Initiate the account with the corresponding account number and the required account type"""
        self.account_type = account_type
        self.latest_interest_date = latest_interest_date
    
    def generate_account_number(self, session: Session):
        """
        Generates a unique 9-digit account number.
        """
        last_account = session.query(Account).order_by(Account.account_id.desc()).first()
        self.account_id = last_account.account_id + 1
        if last_account:
            self.account_number = f"{self.account_id:09d}"  
        else:
            self.account_number = "000000001" 
        return self.account_number

    
    def latest_transaction_date(self, session: Session, trans_type = "Common"):
        """This function is used to get the most recent transaction date"""
        stmt = select(Transaction).where(Transaction.account_id == self.account_id, 
                                         Transaction.transaction_type == trans_type).order_by(Transaction.date.desc())
        latest_transaction = session.execute(stmt).scalars().first()
    
        return latest_transaction.date if latest_transaction else None
            

    def get_balance(self, session: Session):
        """This function is used to get the current balance of the selected account. If there have been no transactions yet, 
        the else condition is used to handle the empty transaction records"""
        # transactions = (
        # session.query(Transaction)
        # .filter(Transaction.account_id == self.account_id)
        # .all()
        # )
        # if transactions:
        #     total_balance = sum(transactions)
        # else:
        #     total_balance = Decimal(0.00)

        return Decimal(self.balance)

    def display(self, session: Session) -> str:
        """Use to show the information including account type, account number and current balance of the selected account"""
        current_total = self.get_balance(session).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{self.account_type[0].upper() + self.account_type[1:]}#{self.account_number},\tbalance: ${current_total:,.2f}"


    def list_transactions(self, session: Session) -> str:
        """Return the transactions from the earliest to latest in the format as required"""
        history = (
        session.query(Transaction)
        .filter(Transaction.account_id == self.account_id)
        .all()
        )
        sorted_history = sorted(history)
        transations = ""
        for i in range(len(sorted_history)):
            t = sorted_history[i]
            transations += str(t)
            if i < len(sorted_history) - 1:
                transations += "\n"
        return transations
                
            