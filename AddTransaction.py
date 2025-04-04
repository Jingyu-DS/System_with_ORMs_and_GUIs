
from utils import validate_date
import logging
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from exceptions import OverdrawError, TransactionLimitError, TransactionSequenceError


class AddTransactionDialog(tk.Toplevel):
    """Dialog for adding a transaction"""
    def __init__(self, parent, session, selected_account):
        super().__init__(parent)
        self.session = session
        self.selected_account = selected_account
        self.title("Add Transaction")
        self.create_widgets()

    def create_widgets(self):
        """Create widgets for the dialog"""
        tk.Label(self, text = "Amount:").pack()
        self.amount_entry = tk.Entry(self)
        self.amount_entry.pack()

        tk.Label(self, text="Date (Select or Type YYYY-MM-DD):").pack()
        self.date_var = tk.StringVar()
        DateEntry(self, width = 12, background = "darkblue", foreground = "white", borderwidth = 2, textvariable = self.date_var, date_pattern = "yyyy-MM-dd").pack()
        tk.Entry(self, textvariable = self.date_var).pack()
        
        tk.Button(self, text = "Submit", command = self._submit_transaction).pack()

    def _submit_transaction(self):
        """Handle transaction submission"""
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric amount.")
            return
        
        date = self.date_var.get()
        if not validate_date(date):
            messagebox.showerror("Date Error", "Please enter a valid date in YYYY-MM-DD format or select a date using the picker.")
            return
        
        try:
            self.selected_account.add_transaction(self.session, amount, date)
            messagebox.showinfo("Success", "Transaction added successfully!")
            logging.debug(f"Created transaction: {self.selected_account.account_number}, {amount}")
            logging.debug("Saved to bank.db")
            self.destroy()
        except OverdrawError:
            messagebox.showerror("Transaction Error", "Insufficient balance for this transaction.")
        except TransactionLimitError as e:
            messagebox.showerror("Transaction Error", f"This transaction could not be completed because this account already has {e.limit_value} transactions in this {e.limit_type}.")
        except TransactionSequenceError as e:
            messagebox.showerror("Transaction Error", f"New transactions must be from {e.latest_transaction_date} onward.")
        except Exception as e:
            messagebox.showerror("Error", "An unexpected error occurred. Check logs.")

