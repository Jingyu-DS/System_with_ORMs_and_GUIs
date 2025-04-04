import logging
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Session

class Base(DeclarativeBase):
    pass


from savings_account import SavingAccount
from checking_account import CheckingAccount
from account import Account
from datetime import datetime
from exceptions import OverdrawError, TransactionLimitError, TransactionSequenceError

class Bank(Base):
    """
    The Bank Class is composed by Saving Account and Checking Account, realizing the functions like open account, 
    summarize the accounts, select account, add transactions, list previous transtions and calculate interests and fees
    """
    __tablename__ = "bank"

    _id = mapped_column(Integer, primary_key=True, default = 1)
    name = mapped_column(String, default="Bank Service")
    accounts = relationship("Account", back_populates="bank", cascade="all, delete-orphan")
    current_account = None


    # def __init__(self):
    #     self.accounts = []
    #     self.current_account = None
    #     self.next_account_number = 1
    

    def menu(self, session: Session) -> str:
        """This is the main menu when a user uses the bank system"""
        return f"""--------------------------------
Currently selected account: {self.current_account.display(session) if self.current_account else "None"}
Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit"""

    def open_account(self, session: Session) -> None:
        """
        This function takes the input from users when users intend to open a new account in the bank. There are two account categories:
        Checking and Savings. 
        """
        try: 
            while True:
                account_type = input("Type of account? (checking/savings)\n>").strip().lower()
            
                if account_type in ["checking", "savings"]:
                    break
                print("Invalid account type. Please enter 'checking' or 'savings'.")

            if account_type == "savings":
                new_account = SavingAccount(account_type)
            if account_type == "checking":
                new_account = CheckingAccount(account_type)
            account_number = new_account.generate_account_number(session)
            session.add(new_account)
            session.commit()
            logging.debug(f"Created account: {account_number}")
            logging.debug("Saved to bank.db")
        
        except Exception as e:
            exception_message = repr(e).replace("\n", "\\n")
            logging.error(f"{type(e).__name__}: {exception_message}")
            print(f"Unexpected error occured: {e}")
        return None


    def summary(self, session: Session):
        """
        This function is to provide a summary of accounts the bank is currently having
        """
        accounts = session.query(Account).all()
        for account in accounts:
            print(account.display(session))

    def select_account(self, session) -> Account:
        """
        When user selects a specific account, the function updates the current account to the newly selected account
        """
        while True: 
            account_number = input("Enter account number\n>")
            try:
                int(account_number)
                break
            except ValueError:
                print("Please try again with a valid account number")
        
        account_number = int(account_number)
        account_number = f"{account_number:09d}"
        account = session.query(Account).filter_by(account_number = account_number).first()
        self.current_account = account
        return self.current_account
    
    def add_transaction(self, session: Session) -> None:
        """
        The function is to take the transactions that the user intends the make. The transaction is composed by the amount and date
        """

        try:
            if self.current_account is None:
                raise AttributeError("This command requires that you first select an account.")
            
            while True:
                amount = input("Amount?\n>")
                try:
                    float(amount)
                    break
                except ValueError:
                    print("Please try again with a valid dollar amount.")
        
            while True:
                date = input("Date? (YYYY-MM-DD)\n>").strip()
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Please try again with a valid date in the format YYYY-MM-DD.")
        
            
            self.current_account.add_transaction(session, float(amount), date)
            logging.debug(f"Created transaction: {self.current_account.account_number}, {amount}")
            logging.debug("Saved to bank.db")
        
        except AttributeError:
            print("This command requires that you first select an account.")
        
        except OverdrawError:
            print("This transaction could not be completed due to an insufficient account balance.")
        
        except TransactionLimitError as e:
            print(f"This transaction could not be completed because this account already has {e.limit_value} transactions in this {e.limit_type}.")
        
        except TransactionSequenceError as e:
            print(f"New transactions must be from {e.latest_transaction_date} onward.")
        
        except Exception as e:
            print(f"Unexpected error occured: {e}")
        
        return None
    
    
    
    def list_transactions(self, session: Session) -> None:
        """
        This function is to list all the past transations have been made from past to the latest
        """
        try:
            if self.current_account is None:
                raise AttributeError("This command requires that you first select an account.")
            print(self.current_account.list_transactions(session))
        
        except AttributeError:
            print("This command requires that you first select an account.")

        except Exception as e:
            print(f"Unexpected error occured: {e}")

        return None

    
    def interests_and_fees(self, session: Session) -> None:
        """
        This function is calculate the interest and fee required for the current account
        """
        try:
            if self.current_account is None:
                raise AttributeError("This command requires that you first select an account.")

            self.current_account.interests_and_fees(session)
            logging.debug("Triggered interest and fees")
            logging.debug("Saved to bank.db")

        except AttributeError:
            print("This command requires that you first select an account.")

        except TransactionSequenceError as e:
            print(f"Cannot apply interest and fees again in the month of {e.latest_transaction_date}.")
        
        except Exception as e:
            print(f"Unexpected error occured: {e}")

        return None



