
from flask import Flask, render_template, request, redirect, url_for
import json, os
from datetime import datetime

app = Flask(__name__)

INVENTORY_FILE = 'inventory.json'
TRANSACTIONS_FILE = 'transactions.json'

def load_json(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    inventory = load_json(INVENTORY_FILE)
    return render_template('index.html', inventory=inventory)

@app.route('/generate', methods=['POST'])
def generate_invoice():
    try:
        name = request.form['name']
        phone = request.form['phone']
        payment_mode = request.form['payment_mode']
        inventory = load_json(INVENTORY_FILE)
        transactions = load_json(TRANSACTIONS_FILE)

        items = []
        total = 0

        for item in inventory:
            code = item['code']
            if request.form.get(f'check_{code}'):
                try:
                    quantity = int(request.form.get(f'quantity_{code}', 0))
                    custom_price = float(request.form.get(f'price_{code}', 0))
                except ValueError:
                    continue
                total += custom_price * quantity
                items.append({
                    'code': code,
                    'name': item['name'],
                    'quantity': quantity,
                    'unit_price': custom_price
                })
                for inv_item in inventory:
                    if inv_item['code'] == code:
                        inv_item['stock'] = max(inv_item['stock'] - quantity, 0)

        if items:
            transactions.append({
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'name': name,
                'phone': phone,
                'items': items,
                'total': total,
                'payment_mode': payment_mode
            })
            save_json(TRANSACTIONS_FILE, transactions)
            save_json(INVENTORY_FILE, inventory)

        return redirect(url_for('index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/transactions')
def transactions():
    try:
        transactions = load_json(TRANSACTIONS_FILE)
        customers = {(txn['name'], txn['phone']) for txn in transactions if 'name' in txn and 'phone' in txn}
        customers = sorted(customers)
        for txn in transactions:
            txn.setdefault('datetime', 'N/A')
            txn.setdefault('name', 'N/A')
            txn.setdefault('phone', 'N/A')
            txn.setdefault('items', [])
            txn.setdefault('total', 0)
            txn.setdefault('payment_mode', 'N/A')
            for item in txn['items']:
                item.setdefault('name', 'N/A')
                item.setdefault('quantity', 0)
                item.setdefault('unit_price', 0)
        return render_template('transactions.html', customers=customers, transactions=transactions)
    except Exception as e:
        return f"Error loading transactions: {str(e)}", 500

@app.route('/inventory')
def inventory():
    inventory = load_json(INVENTORY_FILE)
    return render_template('inventory.html', inventory=inventory)

@app.route('/inventory/update', methods=['POST'])
def update_inventory():
    inventory = load_json(INVENTORY_FILE)
    code = request.form['code']
    name = request.form['name']
    try:
        stock = int(request.form['stock'])
        price = float(request.form['price'])
    except ValueError:
        return "Invalid stock or price", 400
    for item in inventory:
        if item['code'] == code:
            item['name'] = name
            item['stock'] = stock
            item['price'] = price
            break
    else:
        inventory.append({'code': code, 'name': name, 'stock': stock, 'price': price})
    save_json(INVENTORY_FILE, inventory)
    return redirect(url_for('inventory'))

if __name__ == '__main__':
    app.run(debug=True)
