from flask import Flask, request, jsonify, send_file
from bank_class import Bank_account, Saving_account
from Database_cred_and_func import (
    save_account_to_db,
    save_transaction_to_db,
    get_account_details,
    update_balance,
    get_txn_of_cust
)

app = Flask(__name__)

# In-memory session store
sessions = {}

@app.route("/")
def homepage():
    return send_file("bank_app_frontend_flask.html")

@app.route("/signup", methods=["POST","GET"])
def signup():
    data = request.json
    required = ["first_name", "last_name", "email", "password", "balance", "account_type"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing fields"}), 400

    save_account_to_db(
        data["first_name"],
        data["last_name"],
        data["email"],
        data["password"],
        data["balance"],
        data["account_type"]
    )
    return jsonify({"message": f"Account created for {data['first_name']}"})

@app.route("/login", methods=["POST","GET"])
def login():
    data = request.json
    account_details = get_account_details(data["email"], data["password"])
    if not account_details:
        return jsonify({"error": "Invalid credentials"}), 401

    if account_details["account_type"] == "Current_Account":
        account = Bank_account(
            account_details["first_name"],
            account_details["last_name"],
            account_details["email"],
            account_details["password"],
            account_details["balance"]
        )
    else:
        account = Saving_account(
            account_details["first_name"],
            account_details["last_name"],
            account_details["email"],
            account_details["password"],
            account_details["balance"]
        )

    sessions[data["email"]] = account
    return jsonify({"message": "Login successful"})

@app.route("/balance", methods=["GET"])
def balance():
    email = request.args.get("email")
    account = sessions.get(email)
    if not account:
        return jsonify({"error": "Not logged in"}), 403
    return jsonify({"balance": account.check_balance()})

@app.route("/withdraw", methods=["POST"])
def withdraw():
    data = request.json
    account = sessions.get(data["email"])
    if not account:
        return jsonify({"error": "Not logged in"}), 403
    try:
        amount = int(data["amount"])
        account.withdraw_money(amount)
        return jsonify({"message": f"Withdrew {amount}", "balance": account.balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/deposit", methods=["POST"])
def deposit():
    data = request.json
    account = sessions.get(data["email"])
    if not account:
        return jsonify({"error": "Not logged in"}), 403
    try:
        amount = int(data["amount"])
        account.add_money(amount)
        return jsonify({"message": f"Deposited {amount}", "balance": account.balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/transactions')
def get_transactions():
    email = request.args.get('email')
    account = sessions.get(email)

    if not account:
        return jsonify({'error': 'Not logged in'}), 403

    try:
        txn_df = account.get_txns()

        if txn_df.empty:
            return jsonify({'transactions': []})

        # Convert to list of dicts and rename keys
        transactions = txn_df.rename(columns={
            'Customer_txn_number': 'txn_number',
            'txn_type': 'description'
        }).to_dict(orient='records')

        return jsonify({'transactions': transactions})

    except Exception as e:
        print("Error fetching transactions:", e)
        return jsonify({'transactions': [], 'error': 'Failed to retrieve transactions'})

@app.route("/logout", methods=["POST"])
def logout():
    global account
    account = None  # Destroy the account object
    return jsonify({"message": "Logged out"})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000,debug=True)
    
