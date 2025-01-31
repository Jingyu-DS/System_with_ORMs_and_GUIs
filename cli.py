import pickle
import os
import sys
from bank import Bank

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
                print(f"An error occurred: {e}")
    
    def _save(self):
        """
        Saves the bank state to a pickle file
        """
        self.bank.current_account = None
        with open("bank.pickle", "wb") as f:
            pickle.dump(self.bank, f)
        # print("Bank state saved.")
    

    def _load(self):
        """
        Loads the bank state from a file, if it exists
        """

        if os.path.exists("bank.pickle"):
            with open("bank.pickle", "rb") as f:
                self.bank = pickle.load(f)
        #    print("Loaded saved bank state.")
        # else:
        #     print("No saved bank state found. Starting with a new bank.")
        self.bank.current_account = None
    

    def _quit(self):
        """
        Saves the state and exits the program
        """
        self._save()
        sys.exit(0)


if __name__ == "__main__":
    Menu().run()