
import tkinter as tk
from tkinter import ttk
from account import Account


class SummaryDialog(tk.Toplevel):
    """Dialog for displaying account summaries"""
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        self.title("Accounts Summary")
        self.create_widgets()

    def create_widgets(self):
        """Create widgets for the dialog"""
        tree = ttk.Treeview(self, columns = ("Account Number", "Type", "Balance"), show = "headings")
        tree.heading("Account Number", text = "Account Number")
        tree.heading("Type", text = "Type")
        tree.heading("Balance", text = "Balance")
        
        accounts = self.session.query(Account).all()
        for account in accounts:
            tree.insert("", "end", values = (account.account_number, account.account_type, account.balance))
        
        tree.pack()
        tk.Button(self, text="Close", command = self.destroy).pack()