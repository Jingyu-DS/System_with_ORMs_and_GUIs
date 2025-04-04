
import tkinter as tk
import logging
from tkinter import messagebox
from savings_account import SavingAccount
from checking_account import CheckingAccount



class OpenAccountDialog(tk.Toplevel):
    """Dialog for opening a new account"""
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        self.title("Open Account")
        self.create_widgets()

    def create_widgets(self):
        """Create widgets for the dialog"""
        tk.Label(self, text="Select Account Type:").pack()
        self.account_type_var = tk.StringVar(value = "checking")
        
        tk.Radiobutton(self, text = "Checking", variable = self.account_type_var, value = "checking").pack()
        tk.Radiobutton(self, text = "Savings", variable = self.account_type_var, value = "savings").pack()
        
        tk.Button(self, text = "Submit", command = self._submit_account_type).pack()

    def _submit_account_type(self):
        """Handle account type submission"""
        account_type = self.account_type_var.get()
        if account_type == "savings":
            new_account = SavingAccount(account_type)
        else:
            new_account = CheckingAccount(account_type)
        
        account_number = new_account.generate_account_number(self.session)
        self.session.add(new_account)
        self.session.commit()
        logging.debug(f"Created account: {account_number}")
        logging.debug("Saved to bank.db")
        messagebox.showinfo("Success", f"{account_type.capitalize()} account created successfully!")
        self.destroy()