import pickle
import os
import sys
import logging
from bank import Bank

logging.basicConfig(
    filename = "bank.log",
    level = logging.DEBUG,
    format = "%(asctime)s|%(levelname)s|%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Menu:
    """
    This Menu class is used to handle the menu and program running logic for the banking system based on the users' inputs
    """

    def __init__(self):
        """Initializes the notebook. If there is a local save file named notebook.pickle, we load it in.
        Otherwise, it creates a new notebook
        """

        self.bank = Bank()
        self._load()
    
    def run(self):
        """
        Main running logic function to show the menu, get the input from users, take actions based on the input
        """
        while True:
            try:
                print(self.bank.menu())
                command = input(">").strip()
                if command == "1":
                    self.bank.open_account()
                elif command == "2":
                    self.bank.summary()
                elif command == "3":
                    self.bank.select_account()
                elif command == "4":
                    self.bank.add_transaction()
                elif command == "5":
                    self.bank.list_transactions()
                elif command == "6":
                    self.bank.interests_and_fees()
                elif command == "7":
                    self._quit()
                else:
                    print("Invalid command.")
            except Exception as e:
                exception_message = repr(e).replace("\n", "\\n")
                logging.error(f"{type(e).__name__}: {exception_message}")
    
    def _save(self):
        """
        Saves the bank state to a pickle file
        """
        self.bank.current_account = None
        with open("bank.pickle", "wb") as f:
            pickle.dump(self.bank, f)
        logging.debug("Saved to bank.pickle")
    

    def _load(self):
        """
        Loads the bank state from a file, if it exists
        """

        if os.path.exists("bank.pickle"):
            with open("bank.pickle", "rb") as f:
                self.bank = pickle.load(f)
            logging.debug("Loaded from bank.pickle")
        self.bank.current_account = None
    

    def _quit(self):
        """
        Saves the state and exits the program
        """
        self._save()
        sys.exit(0)


if __name__ == "__main__":
    try:
        Menu().run()
    except Exception as e:
        exception_message = repr(e).replace("\n", "\\n")
        logging.error(f"{type(e).__name__}: {exception_message}")
        sys.exit(1)
