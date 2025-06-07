
from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)

DATA_DIR = 'data'
INVENTORY_FILE = os.path.join(DATA_DIR, 'inventory.json')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    inventory = load_json(INVENTORY_FILE)
    return render_template('index.html', inventory=inventory)

@app.route('/generate', methods=['POST'])
def generate_invoice():
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
            quantity = int(request.form.get(f'quantity_{code}', 0))
            custom_price = float(request.form.get(f'price_{code}', 0))
            total += custom_price * quantity
            items.append({
                'code': code,
                'name': item['name'],
                'quantity': quantity,
                'unit_price': custom_price
            })
            for i in inventory:
                if i['code'] == code:
                    i['stock'] -= quantity

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

@app.route('/transactions')
def transactions():
    transactions = load_json(TRANSACTIONS_FILE)
    customers = list({(t['name'], t['phone']) for t in transactions})
    return render_template('transactions.html', transactions=transactions, customers=customers)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    inventory = load_json(INVENTORY_FILE)
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        for item in inventory:
            if item['code'] == code:
                item['name'] = name
                item['price'] = price
                item['stock'] = stock
                break
        else:
            inventory.append({'code': code, 'name': name, 'price': price, 'stock': stock})

        save_json(INVENTORY_FILE, inventory)
        return redirect(url_for('inventory'))

    return render_template('inventory.html', inventory=inventory)

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(INVENTORY_FILE):
        save_json(INVENTORY_FILE, [
            {'code': 'P001', 'name': 'Widget', 'price': 10.0, 'stock': 100},
            {'code': 'P002', 'name': 'Gadget', 'price': 20.0, 'stock': 50},
            {'code': 'P003', 'name': 'Thingamajig', 'price': 15.5, 'stock': 75}
        ])
    if not os.path.exists(TRANSACTIONS_FILE):
        save_json(TRANSACTIONS_FILE, [])
    app.run(debug=True, host='0.0.0.0')
