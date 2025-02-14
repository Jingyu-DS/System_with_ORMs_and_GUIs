from decimal import Decimal, ROUND_HALF_UP

class Account:
    """The Account Class is used as a parent class for both Checking and Saving Accouts to realize several fundemantal functions
    Including the get balance, list transactions, display the current information for the account. Adding transactions and getting
    interests and fees functions are different between checking and saving accounts. Thus, they will be realized in the child classes"""
    
    def __init__(self, account_type: str, account_number: int, latest_interest_date = None):
        """Initiate the account with the corresponding account number and the required account type"""
        self.account_type = account_type
        self.account_num = account_number
        self.account_number = f"{account_number:09d}"
        # tansaction is a transaction object
        self.transactions = []
        self.latest_interest_date = latest_interest_date
    
    def latest_transaction_date(self):
        """This function is used to get the most recent transaction date"""
        if not self.transactions:
            return None
        latest_transaction = max(self.transactions)
        return latest_transaction.date
            

    def get_balance(self):
        """This function is used to get the current balance of the selected account. If there have been no transactions yet, 
        the else condition is used to handle the empty transaction records"""
        if self.transactions:
            total = sum(self.transactions)
        else:
            total = Decimal(0.00)
        return total

    def display(self) -> str:
        """Use to show the information including account type, account number and current balance of the selected account"""
        current_total = self.get_balance().quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{self.account_type[0].upper() + self.account_type[1:]}#{self.account_number},\tbalance: ${current_total:,.2f}"


    def list_transactions(self) -> str:
        """Return the transactions from the earliest to latest in the format as required"""
        self.transactions.sort()
        transations = ""
        for i in range(len(self.transactions)):
            t = self.transactions[i]
            transations += str(t)
            if i < len(self.transactions) - 1:
                transations += "\n"
        return transations
                
            
