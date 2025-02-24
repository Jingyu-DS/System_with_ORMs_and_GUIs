import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkcalendar import DateEntry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bank import Bank, Base
import logging
from transactions import Transaction
from excpetions import OverdrawError, TransactionLimitError, TransactionSequenceError
from account import Account
from savings_account import SavingAccount
from checking_account import CheckingAccount

logging.basicConfig(
    filename = "bank.log",
    level = logging.DEBUG,
    format = "%(asctime)s|%(levelname)s|%(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

engine = create_engine("sqlite:///bank.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
session = Session()

class BankGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MY BANK")
        self.bank = session.get(Bank, 1)
        if self.bank is None:
            self.bank = Bank()
            session.add(self.bank)
            session.commit()
        self.selected_account = None
        self.create_widgets()
    

    def create_widgets(self):
        self.header = tk.Label(self.root, text="Selected account:", font=("Arial", 12), bg="lightgray")
        self.header.pack(fill=tk.X)
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        buttons = [
            ("Open Account", self.open_account),
            ("Summary", self.show_summary),
            ("Select Account", self.select_account),
            ("List Transactions", self.list_transactions),
            ("Add Transaction", self.add_transaction),
            ("Interest and Fees", self.apply_interest_fees),
            ("Quit", self.quit_app)
        ]
        for text, command in buttons:
            btn = tk.Button(self.frame, text = text, command = command, width = 15)
            btn.pack(side = tk.LEFT, padx = 5, pady = 5)
    
    def open_account(self):
        top = tk.Toplevel(self.root)
        top.title("Open Account")  
        tk.Label(top, text = "Select Account Type:").pack()
        account_type_var = tk.StringVar(value = "checking")
        
        checking_radio = tk.Radiobutton(top, text = "Checking", variable = account_type_var, value = "checking")
        savings_radio = tk.Radiobutton(top, text = "Savings", variable = account_type_var, value = "savings")
        checking_radio.pack()
        savings_radio.pack()
        
        def submit_account_type():
            account_type = account_type_var.get()
            if account_type == "savings":
                new_account = SavingAccount(account_type)
            if account_type == "checking":
                new_account = CheckingAccount(account_type)
            account_number = new_account.generate_account_number(session)
            session.add(new_account)
            session.commit()
            logging.debug(f"Created account: {account_number}")
            messagebox.showinfo("Success", f"{account_type.capitalize()} account created successfully!")
            top.destroy()
        
        submit_button = tk.Button(top, text = "Submit", command = submit_account_type)
        submit_button.pack()


    def show_summary(self):
        top = tk.Toplevel(self.root)
        top.title("Accounts Summary")
        tree = ttk.Treeview(top, columns=("Account Number", "Type", "Balance"), show="headings")
        tree.heading("Account Number", text="Account Number")
        tree.heading("Type", text="Type")
        tree.heading("Balance", text="Balance")
        
        accounts = session.query(Account).all()
        for account in accounts:
            tree.insert("", "end", values=(account.account_number, account.account_type, account.balance))
        
        tree.pack()
        close_button = tk.Button(top, text="Close", command=top.destroy)
        close_button.pack()
    
    
    def select_account(self):
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
                self.header.config(text = f"Selected account: {self.selected_account.account_number}")
                messagebox.showinfo("Success", "Account selected!")
            else:
                # logging.warning(f"Attempted to select non-existent account {account_number}.")
                messagebox.showerror("Error", "Account not found!")
    
    
    def list_transactions(self):
        if not self.selected_account:
            # logging.error("Transaction list requested without selecting an account.")
            messagebox.showerror("Error", "This command requires that you first select an account.")
            return
        history = (
            session.query(Transaction)
            .filter(Transaction.account_id == self.selected_account.account_id)
            .all()
        )
        sorted_history = sorted(history)
        self.display_transactions(sorted_history)
    
    def display_transactions(self, transactions):
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
    
    def add_transaction(self):
        if not self.selected_account:
            # logging.error("Transaction attempted without selecting an account.")
            messagebox.showerror("Error", "This command requires that you first select an account.")
            return
        
        top = tk.Toplevel(self.root)
        top.title("Add Transaction")
        tk.Label(top, text = "Amount:").pack()
        amount_entry = tk.Entry(top)
        amount_entry.pack()
        tk.Label(top, text = "Date:").pack()
        date_picker = DateEntry(top, width = 12, background = "darkblue", foreground = "white", borderwidth = 2)
        date_picker.pack()
        
        def submit_transaction():
            try:
                amount = float(amount_entry.get())
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid numeric amount.")
            
            try:
                date = date_picker.get_date().strftime("%Y-%m-%d")
                self.selected_account.add_transaction(session, amount, date)
                messagebox.showinfo("Success", "Transaction added successfully!")
                top.destroy()
            
            except OverdrawError:
                messagebox.showerror("Transaction Error", "Insufficient balance for this transaction.")
            except TransactionLimitError as e:
                messagebox.showerror("Transaction Error", f"This transaction could not be completed because this account already has {e.limit_value} transactions in this {e.limit_type}.")
            except TransactionSequenceError as e:
                messagebox.showerror("Transaction Error", f"New transactions must be from {e.latest_transaction_date} onward.")
            except Exception as e:
                messagebox.showerror("Error", "An unexpected error occurred. Check logs.")
        
        submit_button = tk.Button(top, text = "Submit", command = submit_transaction)
        submit_button.pack()
    
    def apply_interest_fees(self):
        if not self.selected_account:
            # logging.error("Interest and fees calculation attempted without selecting an account.")
            messagebox.showerror("Error", "This command requires that you first select an account.")
            return
        try:
            self.selected_account.interests_and_fees(session)
            messagebox.showinfo("Success", "Interest and fees applied!")
        
        except TransactionSequenceError as e:
            messagebox.showerror("Error", f"Cannot apply interest and fees again in the month of {e.latest_transaction_date}.")
    
    def quit_app(self):
        session.commit()
        session.close()
        logging.info("Application closed.")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BankGUI(root)
    root.mainloop()