import pandas as pd
import Database_cred_and_func as dbf


class Bank_account:

    def __init__(self, first_name: str, last_name: str, email: str, password: str, deposit: int):
        # Validation check
        parameters = [first_name, last_name, email, password]
        for i in parameters:
            assert type(i) == str, f'{i} is not a string'
        assert deposit > 0, f'The deposit needs to be greater than 0'
        

        # Assign the account user details
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.email = email
        self.balance = deposit

        # get the account number to make later changes
        account_details = dbf.get_account_details(email,password)
        self.account_number = account_details['account_number'] 

    def add_money(self, add_amount: int):
        self.balance += add_amount
        dbf.save_transaction_to_db(self.account_number, 'Deposit',add_amount)
        dbf.update_balance(self.account_number,self.balance)

    def withdraw_money(self, withdraw_amount: int):
        if withdraw_amount <= self.balance:
            self.balance -= withdraw_amount
            dbf.save_transaction_to_db(self.account_number, 'Withdraw',withdraw_amount)
            dbf.update_balance(self.account_number,self.balance)
        else:
            print("Insufficient balance!")

    def check_balance(self):
        return self.balance
    
    def get_txns(self):
        self.txn_database = dbf.get_txn_of_cust(self.account_number)
        self.txn_database['Customer_txn_number'] = self.txn_database.index + 1
        return self.txn_database[['Customer_txn_number','txn_type','amount']]
    
    # @classmethod
    # def all_accounts(cls):
        # print(cls.bank_db)

    @classmethod
    def read_all_records(cls):
        pass

class Saving_account(Bank_account):
    def __init__(self, first_name: str, last_name: str, email: str, password: str, deposit: int):
        super().__init__(first_name, last_name, email, password, deposit)

    def withdraw_money(self, withdraw_amount: int):
        fee = 2  # Savings accounts have a fee
        total_withdraw = withdraw_amount + fee
        if total_withdraw <= self.balance:
            self.balance -= total_withdraw
            # Bank_account.bank_db.at[self.account_number, 'Balance'] = self.balance
        else:
            print("Insufficient balance!")