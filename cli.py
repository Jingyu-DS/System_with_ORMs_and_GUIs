import sys
import logging
from bank import Bank, Base
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker, Session


logging.basicConfig(
    filename = "bank.log",
    level = logging.DEBUG,
    format = "%(asctime)s|%(levelname)s|%(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

class Menu:
    """
    This Menu class is used to handle the menu and program running logic for the banking system based on the users' inputs
    """

    def __init__(self, session):
        """Initializes the notebook. If there is a local save file named notebook.pickle, we load it in.
        Otherwise, it creates a new notebook
        """
        self._session = session
        self.bank = self._session.get(Bank, 1)
        if self.bank is None:
            self.bank = Bank()
            self._session.add(self.bank)
            self._session.commit()
            logging.debug("Saved to bank.db")
        else:
            logging.debug("Loaded from bank.db")
        
    
    def run(self):
        """
        Main running logic function to show the menu, get the input from users, take actions based on the input
        """
        while True:
            print(self.bank.menu(self._session))
            command = input(">").strip()
                
            if command == "1":
                self.bank.open_account(self._session) 
            elif command == "2":
                self.bank.summary(self._session)
            elif command == "3":
                self.bank.select_account(self._session)
            elif command == "4":
                self.bank.add_transaction(self._session) 
            elif command == "5":
                self.bank.list_transactions(self._session)
            elif command == "6":
                self.bank.interests_and_fees(self._session) 
            elif command == "7":
                self._quit()
            else:
                raise EOFError("EOF when reading a line")


    def _quit(self):
        """
        Saves the state and exits the program
        """
        try:
            self._session.commit()
        except Exception as e:
            logging.error(f"Commit error: {repr(e)}")
        finally:
            self._session.close()
        sys.exit(0)


if __name__ == "__main__":
    try:
        engine = create_engine("sqlite:///bank.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        Menu(session).run()
    
    except EOFError as e:
        logging.error(f"{type(e).__name__}: '{str(e)}'")
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        sys.exit(0)

    except Exception as e:
        exception_message = repr(e).replace("\n", "\\n")
        logging.error(f"{type(e).__name__}: {exception_message}")
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        sys.exit(0)
