import urllib.request
import json
import time

backend_base = 'https://api-tracker.samzhoserv.duckdns.org/api/v1'

# 1. Dev Auth
print('--- 1. Testing Auth ---')
req = urllib.request.Request(
    f'{backend_base}/auth/telegram/dev',
    data=json.dumps({'user_id': 99999, 'username': 'test_admin', 'first_name': 'Tester'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    token = data['access_token']
    user_id = data['user']['id']
    print(f'Auth Status: {resp.status}, User ID: {user_id}')

# 2. Get Me
print('--- 2. Testing /auth/me ---')
req = urllib.request.Request(
    f'{backend_base}/auth/me',
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req) as resp:
    me = json.loads(resp.read().decode())
    print(f'/auth/me Status: {resp.status}, Username: {me.get("username")}')

# 3. Get Categories
print('--- 3. Testing /categories ---')
req = urllib.request.Request(
    f'{backend_base}/categories',
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req) as resp:
    cats = json.loads(resp.read().decode())
    print(f'/categories Status: {resp.status}, Count: {len(cats)}')
    food_cat = next((c for c in cats if 'Food' in c.get('name', '')), cats[0])

# 4. Create Expense
print('--- 4. Testing /expenses POST ---')
expense_data = {
    'type': 'expense',
    'amount': 120.75,
    'currency': 'USD',
    'category_id': food_cat['id'],
    'comment': 'Live verification test via HTTPS domain',
    'payment_method': 'card',
    'transaction_date': '2026-10-26T12:38:00'
}
req = urllib.request.Request(
    f'{backend_base}/expenses',
    data=json.dumps(expense_data).encode(),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as resp:
    created_tx = json.loads(resp.read().decode())
    tx_id = created_tx.get('id')
    print(f'Create Expense Status: {resp.status}, TX ID: {tx_id}, Amount: {created_tx.get("amount")}')

# 5. List Expenses
print('--- 5. Testing /expenses GET ---')
req = urllib.request.Request(
    f'{backend_base}/expenses?limit=10',
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req) as resp:
    tx_list = json.loads(resp.read().decode())
    print(f'List Expenses Status: {resp.status}, Total retrieved: {len(tx_list)}')

# 6. Delete Expense
print('--- 6. Testing /expenses DELETE ---')
req = urllib.request.Request(
    f'{backend_base}/expenses/{tx_id}',
    headers={'Authorization': f'Bearer {token}'},
    method='DELETE'
)
with urllib.request.urlopen(req) as resp:
    print(f'Delete Expense Status: {resp.status}')

print('--- ALL BUSINESS LOGIC TESTS PASSED PERFECTLY ---')
