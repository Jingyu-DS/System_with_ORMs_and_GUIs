from decimal import Decimal

class Transaction:
    """This class is designed to indicate a transaction. It will handle the functions including
    the display of each transaction, decision related to how to sort the transactions in the account"""

    _count = 0

    def __init__(self, date: str, amount: float):
        """Initiate a transaction"""
        self.date = date
        self._id = Transaction._count
        self.amount = Decimal(amount)
        Transaction._count += 1
    
    def __str__(self) -> str:
        """Formats the date and amount of this transaction"""
        return f"{self.date}, ${self.amount:,.2f}"

    def __lt__(self, other) -> bool:
        """This function is to ensure the order of sorting and getting the most recent transaction"""
        if self.date == other.date:
            return self._id < other._id
        return self.date < other.date
    

    def __radd__(self, other) -> Decimal:
        """Allows transactions to be summed by their amounts."""
        return other + self.amount
    




    

