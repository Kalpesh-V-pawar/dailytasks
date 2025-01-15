import os
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)

# MongoDB Atlas connection string
mongo_uri = os.getenv("MONGO_URI") 
client = MongoClient(mongo_uri)

# Select your database and collection
db = client["inventory_db"]
inventory_collection = db["inventory"]
transactions_collection = db["transactions"]
users_collection = db['users']



logged_in_user = None


LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
            background-size: 300% 300%;
            animation: gradientBG 10s ease infinite;
            color: #ffffff;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 400px;
            width: 100%; /* Ensures responsiveness */
            background : linear-gradient(135deg, #30343F, #404452);
            margin: 20px auto;
            padding: 30px;
            border-radius: 25px;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3); /* Adds depth */
            color: white;
            min-height : 400px
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            font-size: 16px;
        }
      
        h1, h2 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        .form-group {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            color: white
        }

        select, input {
            padding: 10px;
            width: 100%;
            margin-bottom: 18px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 12px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 18px;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: orange;
        }

        .error {
            color: #dc3545;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            text-align: center;
        }

        .success {
            color: #28a745;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form method="POST">
            <label for="username">Select Username:</label>
            <select id="username" name="username" required>
                <option value="" selected disabled>Select User</option>
                <!-- Regular Users Section -->
                <optgroup label="Users">
                    {% for user in users %}
                        <option value="{{ user }}">{{ user }}</option>
                    {% endfor %}
                </optgroup>

                <!-- Admins Section -->
                <optgroup label="Admins">
                    {% for admin in admins %}
                        <option value="{{ admin }}">{{ admin }}</option>
                    {% endfor %}
                </optgroup>
            </select>
            
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br><br>
            
            <button type="submit">Login</button>
        </form>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>

"""


# Updated form HTML with reason field
form_html = '''
    <html>
    <head>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background:linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
                background-size: 300% 300%;
                animation: gradientBG 10s ease infinite; 
                margin: 0;
                padding: 0;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
              
            }
            
            @keyframes gradientBG {
              0% { background-position: 0% 50%; }
              50% { background-position: 100% 50%; }
              100% { background-position: 0% 50%; }
            }
            
            .container {
                max-width: 800px;
                background: linear-gradient(135deg, #30343F, #404452);
                backdrop-filter: blur(12px);
                margin: 50px auto;
                background-color: #f4f4f4;
                border-radius: 15px;
                padding: 40px;
                
                animation: gradientBG 5s ease infinite; 
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                border-radius: 30px;
                background-size: 200% 200%;
            }
            
            @keyframes containerGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }                
              
            .container:hover{
              color: linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
              animation: gradientBG 10s ease infinite;
            }
            
            h1 {
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 30px;
                color: white
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
                color: white
            }
          
            label {
                font-size: 18px;
                color:white;
            }
            input[type="text"], input[type="number"], select {
                padding: 10px;
                width: 100%;
                margin-bottom: 18px;
                border-radius: 5px;
                border: 1px solid #ccc;
                background-color: #fff;
                color: linear-gradient(135deg, #2e323d, #3a3e4a);
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s ease-in-out;
            }
            input[type="text"]:focus, input[type="number"]:focus, select:focus {
                border-color: linear-gradient(135deg, #383c48, #464a56);
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
                transition: background-color 0.1s ease-in-out;
            }
            input[type="submit"]:hover {
                background-color: orange;
            }
            a {
                text-decoration: none;
                color: #4CAF50;
                text-align: left;
                display: block;
                margin-top: 20px;
                font-size: 18px;
                transition: color 0.1s ease-in-out;
            }
            a:hover {
                color: orange;
            }
            .field-group {
                width: 100%;
                max-width: 350px;
                margin-bottom: 15px;
            }
            select {
                width: 100%;
                max-width: 420px;
                margin-bottom: 15px;
                
                
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Stock Record Chatbot</h1>
            <form method="POST" action="/add">
                <div class="field-group">
                    <label for="item_name">Item Name:</label>
                    <input type="text" id="item_name" name="item_name" required>
                </div>
                
                <div class="field-group">
                    <label for="quantity">Quantity:</label>
                    <input type="number" id="quantity" name="quantity" required>
                </div>
                
                <div class="field-group">
                    <label for="reason">Reason:</label>
                    <select id="reason" name="reason" required>
                        <option value="">Select a reason</option>
                        <option value="New stock arrival">New stock arrival</option>
                        <option value="Restocking">Restocking</option>
                        <option value="Inventory correction">Inventory correction</option>
                        <option value="Damaged goods replacement">Damaged goods replacement</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                
                <div class="field-group" id="other-reason-group" style="display: none;">
                    <label for="other_reason">Specify Other Reason:</label>
                    <input type="text" id="other_reason" name="other_reason">
                </div>
                
                <div class="field-group">
                    <label for="region">Region:</label>
                    <select id="region" name="region" required>
                        <option value="">Select a region</option>
                        <option value="North I">North I</option>
                        <option value="North II">North II</option>
                        <option value="West I">West I</option>
                        <option value="West II">West II</option>
                        <option value="Central India">Central India</option>
                        <option value="South I">South I</option>
                        <option value="South II">South II</option>
                    </select>
                </div>

                <input type="submit" value="Add Item">
            </form>
            <p>Use the form above to add inventory. You can also check inventory status via Postman or cURL.</p>
            <p>For example: <a href="/check?item_name=XYZ">/check?item_name=XYZ</a></p>
            <br><br>
            <h2>Inventory List</h2>
            <a href="/inventory">View All Inventory</a>
        </div>
        
        <script>
            document.getElementById('reason').addEventListener('change', function() {
                var otherReasonGroup = document.getElementById('other-reason-group');
                if (this.value === 'Other') {
                    otherReasonGroup.style.display = 'block';
                } else {
                    otherReasonGroup.style.display = 'none';
                }
            });
        </script>
    </body>
    </html>'''
# HTML Template for displaying inventory with updated colors
inventory_html = '''
    <html>
    <head>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background:linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
                background-size: 300% 300%;
                animation: gradientBG 10s ease infinite; 
                margin: 0;
                padding: 0;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
              
            }
            
            @keyframes gradientBG {
              0% { background-position: 0% 50%; }
              50% { background-position: 100% 50%; }
              100% { background-position: 0% 50%; }
            }
            
            .container {
                max-width: 1400px;
                background: linear-gradient(135deg, #30343F, #404452);
                backdrop-filter: blur(12px);
                margin: 50px auto;
                background-color: #f4f4f4;
                border-radius: 15px;
                padding: 40px;
                
                animation: gradientBG 5s ease infinite; 
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                border-radius: 30px;
                background-size: 200% 200%;
            }
            
            @keyframes containerGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            h1 {
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 30px;
            }
            .inventory-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 30px;
            }
            .inventory-table th, .inventory-table td {
                padding: 15px;
                border: 1px solid #ddd;
                text-align: center;
                vertical-align: middle;
                color: #555;
              
            }
            .inventory-table th {
                background-color: #333;
                color: white;
                font-size: 18px;
            }
            
            
            .inventory-table td {
                font-size: 16px;
            }
            
            .inventory-table tr {
                background-color: #f9f9f9;
                color: black;
            }
            
            .inventory-table tr:hover {
              background-color : #e0e0e0 ;
            }
            
            a {
                text-decoration: none;
                color: #4CAF50;
                display: block;
                text-align: center;
                margin-top: 5px;
                font-size: 18px;
                transition: color 0.3s ease-in-out;
                
            }
            a:hover {
                color: orange;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Inventory List</h1>
            <table class="inventory-table">
                <tr>
                    <th>Item Name</th>
                    <th>Remaining Quantity</th>
                    <th>Total Quantity</th>
                    <th>Used1 Quantity</th>
                    <th>Last Updated</th>
                </tr>
                {% for item in items %}
                <tr>
                    <td><a href="/transactions/{{ item['item_name'] }}">{{ item['item_name'] }}</a></td>
                    <td>{{ item['quantity'] }}</td>
                    <td>{{ item['Total'] }}</td>
                    <td>{{ item['used_quantity'] }}</td>
                    <td>{{ item['last_updated'] }}</td>
                </tr>
                {% endfor %}
            </table>
            <br><br>
            <a href="/">Go Back to Add Inventory</a>
        </div>
    </body>
    </html>
'''

# HTML Template for displaying transaction history
transaction_html = '''
    <html>
    <head>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background: linear-gradient(135deg, #6e7fd5, #b8c1ec);
                margin: 0;
                padding: 0;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 50px auto;
                background-color: #f4f4f4;
                border-radius: 10px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 30px;
            }
            .transaction-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 30px;
            }
            .transaction-table th, .transaction-table td {
                padding: 15px;
                border: 1px solid #ddd;
                text-align: center;
                color: #555;
            }
            .transaction-table th {
                background-color: #333;
                color: white;
                font-size: 18px;
            }
            .transaction-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .transaction-table tr:hover {
                background-color: #e0e0e0;
            }
            .transaction-table td {
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Transaction History for {{ item_name }}</h1>
            <table class="transaction-table">
                <tr>
                    <th>Transaction ID</th>
                    <th>Date</th>
                    <th>Quantity Changed</th>
                    <th>Reason</th>
                    <th>Region</th>

                </tr>
                {% for transaction in transactions %}
                <tr>
                    <td>{{ transaction['transaction_id'] }}</td>
                    <td>{{ transaction['date'] }}</td>
                    <td>{{ transaction['quantity_changed'] }}</td>
                    <td>{{ transaction['reason'] }}</td>
                    <td>{{ transaction['region'] }}</td>
                </tr>
                {% endfor %}
            </table>
            <br><br>
            <a href="/inventory">Go Back to Inventory</a>
        </div>
    </body>
    </html>
'''


@app.route("/", methods=["GET", "POST"])
def login():
    users = {}
    admins = {}

    # Fetch users from MongoDB
    user_data = users_collection.find({"role": "user"}, {"_id": 0, "username": 1, "password": 1})
    for user in user_data:
        users[user["username"]] = {"password": user["password"], "role": "user"}

    # Fetch admins from MongoDB
    admin_data = users_collection.find({"role": "admin"}, {"_id": 0, "username": 1, "password": 1})
    for admin in admin_data:
        admins[admin["username"]] = {"password": admin["password"], "role": "admin"}

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if username is in users or admins
        if username in users and users[username]["password"] == password:
            # Redirect based on the role
            if users[username]["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        elif username in admins and admins[username]["password"] == password:
            # Admin login
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password. Please try again."
            return render_template_string(LOGIN_PAGE, error=error, users=users.keys(), admins=admins.keys())

    return render_template_string(LOGIN_PAGE, users=users.keys(), admins=admins.keys())


# User Dashboard route
@app.route("/user_dashboard")
def user_dashboard():
    return render_template_string(form_html)

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template_string(LOGIN_PAGE)

def record_transaction(item_name, quantity_changed, reason, region):
    """Helper function to record transactions"""
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "item_name": item_name,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "quantity_changed": quantity_changed,
        "reason": reason,
        "region" : region
    }
    transactions_collection.insert_one(transaction)



#@app.route('/')
#def main():
   #return render_template_string(form_html)

@app.route('/add', methods=['POST'])
def add_item():
    item_name = request.form.get('item_name')
    quantity = int(request.form.get('quantity'))
    reason = request.form.get('reason')
    region = request.form.get('region')
    
    # Handle "Other" reason
    if reason == "Other":
        other_reason = request.form.get('other_reason')
        if other_reason:
            reason = other_reason
    
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if the item exists in the inventory
    existing_item = inventory_collection.find_one({"item_name": item_name})


    if existing_item:
        # If the item exists, update the quantity
        total_qty = None
        new_quantity = existing_item['quantity'] + quantity
        if quantity >= 1 :
            if total_qty is not None :
                total_qty = existing_item['Total'] + quantity
            else :
                total_qty = new_quantity   
        else :
            if total_qty is not None :
                total_qty = existing_item['Total']
            else :
                total_qty = existing_item['quantity']    
        used_quantity = total_qty - new_quantity


        inventory_collection.update_one(
            {"item_name": item_name},
            {"$set": {"quantity": new_quantity, "last_updated": last_updated, "Total": total_qty, "used_quantity": used_quantity, "region": region }}
        )
        # Record transaction for update
        record_transaction(
            item_name=item_name,
            quantity_changed=quantity,
            reason=reason,
            region=region
        )
    else:
        # If the item doesn't exist, insert it as a new record
        inventory_collection.insert_one({
            "item_name": item_name,
            "quantity": quantity,
            "last_updated": last_updated,
            "Total" : quantity,
            "used_quantity" : 0,
            "region" : region
        })
        # Record transaction for new item
        record_transaction(
            item_name=item_name,
            quantity_changed=quantity,
            reason=reason,
            region=region
        )

    return render_template_string(form_html)

@app.route('/inventory')
def inventory():
    items = inventory_collection.find()
    items_list = []
    for item in items:
        if 'last_updated' not in item:
            item['last_updated'] = "Not Available"
        items_list.append(item)
    return render_template_string(inventory_html, items=items_list)

@app.route('/transactions/<item_name>')
def transaction_history(item_name):
    transactions = transactions_collection.find(
        {"item_name": item_name}
    ).sort("date", -1)
    
    transaction_list = list(transactions)
    return render_template_string(transaction_html, 
                                item_name=item_name, 
                                transactions=transaction_list)

if __name__ == '__main__':
    app.run(debug=True)
