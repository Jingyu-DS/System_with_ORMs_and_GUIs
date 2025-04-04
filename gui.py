import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bank import Bank, Base
import logging
from transactions import Transaction
from exceptions import TransactionSequenceError
from account import Account
from OpenAccount import OpenAccountDialog
from Summary import SummaryDialog
from AddTransaction import AddTransactionDialog

# Configure logging
logging.basicConfig(
    filename = "bank.log",
    level = logging.DEBUG,
    format = "%(asctime)s|%(levelname)s|%(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

def handle_exception(exception, value, traceback):
    """Defines a callback function that handles unexpected exceptions"""
    error_message = "Sorry! Something unexpected happened. If this problem persists, please contact our support team for assistance."
    logging.error(f"{exception.__name__}: {repr(value)}")
    messagebox.showerror("Unexpected Error", error_message)
    sys.exit(0)

# Database setup
engine = create_engine("sqlite:///bank.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
session = Session()


class BankGUI:
    """Main GUI class for the bank system"""
    def __init__(self, root):
        """Initialize the GUI components and set up the main window"""
        self.root = root
        self.root.title("MY BANK")
        self.bank = session.get(Bank, 1)
        if self.bank is None:
            self.bank = Bank()
            session.add(self.bank)
            session.commit()
            logging.debug("Saved to bank.db")
        else:
            logging.debug("Loaded from bank.db")
        self.selected_account = None
        self.create_widgets()

    def create_widgets(self):
        """Create interactive buttons on the main window"""
        self.header = tk.Label(self.root, text = "Selected account:", font = ("Arial", 12), bg = "lightgray")
        self.header.pack(fill = tk.X)
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        buttons = [
            ("Open Account", self._open_account),
            ("Summary", self._show_summary),
            ("Select Account", self._select_account),
            ("List Transactions", self._list_transactions),
            ("Add Transaction", self._add_transaction),
            ("Interest and Fees", self._apply_interest_fees),
            ("Quit", self._quit_app)
        ]
        for text, command in buttons:
            btn = tk.Button(self.frame, text = text, command = command, width = 15)
            btn.pack(side = tk.LEFT, padx = 5, pady = 5)

    def _open_account(self):
        """Open the Account Creation Dialog"""
        OpenAccountDialog(self.root, session)

    def _show_summary(self):
        """Open the Account Summary Dialog"""
        SummaryDialog(self.root, session)

    def _select_account(self):
        """Allow users to select an account"""
        account_number = simpledialog.askstring("Select Account", "Enter account number:")
        if account_number:
            try:
                account_number = int(account_number)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid numeric account number.")
                return
            account_number = f"{account_number:09d}"
            account = session.query(Account).filter_by(account_number = account_number).first()
            self.selected_account = account
            if self.selected_account:
                self.header.config(text=f"Selected account: {self.selected_account.account_type}{self.selected_account.account_number}")
                messagebox.showinfo("Success", "Account selected!")
            else:
                messagebox.showerror("Error", "Account not found!")

    def _list_transactions(self):
        """List all transactions for the selected account"""
        if not self.selected_account:
            messagebox.showerror("Error", "This command requires that you first select an account.")
            return
        history = (
            session.query(Transaction)
            .filter(Transaction.account_id == self.selected_account.account_id)
            .all()
        )
        sorted_history = sorted(history)
        self._display_transactions(sorted_history)

    def _display_transactions(self, transactions):
        """Display transactions"""
        top = tk.Toplevel(self.root)
        top.title("Transaction History")
        tree = ttk.Treeview(top, columns = ("Date", "Amount"), show = "headings")
        tree.heading("Date", text = "Date")
        tree.heading("Amount", text = "Amount")
        
        for transaction in transactions:
            color = "red" if transaction.amount < 0 else "green"
            tree.insert("", "end", values = (transaction.date, transaction.amount), tags = (color,))
        
        tree.tag_configure("red", foreground = "red")
        tree.tag_configure("green", foreground = "green")
        tree.pack()

    def _add_transaction(self):
        """Open the Transaction Addition Dialog"""
        if not self.selected_account:
            messagebox.showerror("Error", "This command requires that you first select an account.")
            return
        AddTransactionDialog(self.root, session, self.selected_account)

    def _apply_interest_fees(self):
        """Apply interest and fees to the selected account"""
        if not self.selected_account:
            messagebox.showerror("Error", "This command requires that you first select an account.")
            return
        try:
            self.selected_account.interests_and_fees(session)
            messagebox.showinfo("Success", "Interest and fees applied!")
            logging.debug("Triggered interest and fees")
            logging.debug("Saved to bank.db")
        except TransactionSequenceError as e:
            messagebox.showerror("Error", f"Cannot apply interest and fees again in the month of {e.latest_transaction_date}.")

    def _quit_app(self):
        """Quit the application"""
        session.commit()
        session.close()
        logging.info("Application closed.")
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.report_callback_exception = handle_exception
    app = BankGUI(root)
    root.mainloop()