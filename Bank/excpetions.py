
class OverdrawError(ValueError):
    """Exception raised when users overdraw an account"""
    pass

class TransactionSequenceError(ValueError):
    """Exception raised when the new transaction does not follow a chronological order"""
    def __init__(self, latest_transaction_date):
        self.latest_transaction_date = latest_transaction_date
        super().__init__(f"New transactions must be from {latest_transaction_date} onward.")

class TransactionLimitError(ValueError):
    """Exception raised when daily or monthly limits has been reached"""
    def __init__(self, limit_type: str, limit_value: int):
        self.limit_type = limit_type
        self.limit_value = limit_value
        super().__init__(f"This transaction could not be completed because this account already has {limit_value} transactions in this {limit_type}.")

