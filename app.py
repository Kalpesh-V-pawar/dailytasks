import sys
sys.path.append(r'C:\users\kalpe\appData\roaming\python\python312\site-packages')
from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://Kalpeshpawar:01042001@cluster0.ozahk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Select your database and collection
db = client["inventory_db"]
inventory_collection = db["inventory"]
transactions_collection = db["transactions"]

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
                    <th>Total Quantity</th>
                    <th>Used Quantity</th>
                    <th>Remaining Quantity</th>
                    <th>Last Updated</th>
                </tr>
                {% for item in items %}
                <tr>
                    <td><a href="/transactions/{{ item['item_name'] }}">{{ item['item_name'] }}</a></td>
                    <td>{{ item['quantity'] }}</td>
                    <td>{{ "test" }}</td>
                    <td>{{ "test" }}</td>
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
                </tr>
                {% for transaction in transactions %}
                <tr>
                    <td>{{ transaction['transaction_id'] }}</td>
                    <td>{{ transaction['date'] }}</td>
                    <td>{{ transaction['quantity_changed'] }}</td>
                    <td>{{ transaction['reason'] }}</td>
                </tr>
                {% endfor %}
            </table>
            <br><br>
            <a href="/inventory">Go Back to Inventory</a>
        </div>
    </body>
    </html>
'''


def record_transaction(item_name, quantity_changed, reason):
    """Helper function to record transactions"""
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "item_name": item_name,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "quantity_changed": quantity_changed,
        "reason": reason
    }
    transactions_collection.insert_one(transaction)

@app.route('/')
def main():
    return render_template_string(form_html)

@app.route('/add', methods=['POST'])
def add_item():
    item_name = request.form.get('item_name')
    quantity = int(request.form.get('quantity'))
    reason = request.form.get('reason')
    
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
        new_quantity = existing_item['quantity'] + quantity
        inventory_collection.update_one(
            {"item_name": item_name},
            {"$set": {"quantity": new_quantity, "last_updated": last_updated}}
        )
        # Record transaction for update
        record_transaction(
            item_name=item_name,
            quantity_changed=quantity,
            reason=reason
        )
    else:
        # If the item doesn't exist, insert it as a new record
        inventory_collection.insert_one({
            "item_name": item_name,
            "quantity": quantity,
            "last_updated": last_updated
        })
        # Record transaction for new item
        record_transaction(
            item_name=item_name,
            quantity_changed=quantity,
            reason=reason
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
