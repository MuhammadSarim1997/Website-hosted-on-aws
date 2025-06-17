import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import DictCursor

# Load environment variables from .env
load_dotenv()






# Connect to the PostgreSQL database

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    cursor_factory=DictCursor
)


def save_account_to_db(first_name, last_name, email, password, balance,account_type):
    cursor = None  # Initialize cursor to None
    try:
        global conn  # Use the global connection variable


        cursor = conn.cursor()  # Initialize cursor

        # Execute the insert statement
        cursor.execute('''
            INSERT INTO account ( first_name, last_name, email, password, balance, account_type) 
            VALUES ( %s, %s, %s, %s, %s, %s);
        ''', ( first_name, last_name, email, password, balance, account_type))
        

        conn.commit()  # Commit the transaction
        account_info = get_account_details(email,password)
        assert account_info is not None, "Account retrieval failed — check get_account_details()"
        print("Account info retrieved:", account_info)
        save_transaction_to_db(account_info['account_number'],'Deposit', balance)
    except Exception as e:
        print(f"Error saving account to database: {e}")
    finally:
        if cursor is not None:
            cursor.close()  # Close cursor if it was initialized
        # Do NOT close the connection here; it should remain open for other operations

def save_transaction_to_db(account_number, description, amount):
    cursor = None  # Initialize cursor to None
    try:
        global conn  # Use the global connection variable

        cursor = conn.cursor()  # Initialize cursor

        # Execute the insert statement
        cursor.execute('''
            INSERT INTO transactions (account_number, txn_type, amount) 
            VALUES ( %s, %s, %s);
        ''', (account_number, description,amount ))

        conn.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error saving transaction to database: {e}")
    finally:
        if cursor is not None:
            cursor.close()  # Close cursor if it was initialized
        # Do NOT close the connection here; it should remain open for other operations

def get_account_details(email,password):
    
    # Initialize cursor to None
    cursor = None  
    try:
        # Use the global connection variable
        global conn 

        # Initialize cursor
        cursor = conn.cursor(cursor_factory=DictCursor)  

        # Execute the insert statement
        cursor.execute('''
            select * from account where email = %s and password = %s;
        ''',(email,password))
        # Fetch first row of the query
        account_row = cursor.fetchone()
        account_details = {cursor.description[i].name : account_row[i] for i in range(len(cursor.description))}
        return account_details

    except Exception as e:
        print(f"Error no such email: {e}")
    
    finally:
        if cursor is not None:
            cursor.close()  # Close cursor if it was initialized

def update_balance(account_number,new_balance):
    
    # Initialize cursor to None
    cursor = None  
    try:
        # Use the global connection variable
        global conn 

        # Initialize cursor
        cursor = conn.cursor(cursor_factory=DictCursor)  

        # Execute the insert statement
        cursor.execute('''
            UPDATE account set balance=%s where account_number=%s;
        ''',(new_balance,account_number))
        conn.commit()

    except Exception as e:
        print(f"Error no such account: {e}")
    
    finally:
        if cursor is not None:
            cursor.close()  # Close cursor if it was initialized

def get_txn_of_cust(account_id):
    
    # Initialize cursor to None
    cursor = None  
    try:
        # Use the global connection variable
        global conn 

        # Initialize cursor
        cursor = conn.cursor(cursor_factory=DictCursor)  

        # Execute the insert statement
        cursor.execute('''
            select * from transactions where account_number = %s ;
        ''',(account_id,))
        # Fetch first row of the query
        txn_headings = [cursor.description[i].name  for i in range(len(cursor.description))]
        txns_table = pd.DataFrame(cursor.fetchall(),columns=txn_headings)
        return txns_table

    except Exception as e:
        print(f"Error no such email: {e}")
    
    finally:
        if cursor is not None:
            cursor.close()  # Close cursor if it was initialized








