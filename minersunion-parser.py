import os
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Читаем секрет как чистую JSON-строку
sa_json = os.environ.get('SERVICE_ACCOUNT_JSON')
if not sa_json:
    raise EnvironmentError("SERVICE_ACCOUNT_JSON не задана в env")

# Парсим JSON прямо из строки
sa_info = json.loads(sa_json)

# Читаем ID таблицы
spreadsheet_id = os.environ.get('SPREADSHEET_ID')
if not spreadsheet_id:
    raise EnvironmentError("SPREADSHEET_ID не задана в env")

# Авторизуемся в Google Sheets
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(spreadsheet_id).sheet1

def fetch_all_validators(limit=1000):
    all_items = []
    page = 1
    while True:
        resp = requests.get(
            'https://api.minersunion.ai/validators',
            params={'page': page, 'limit': limit}
        )
        resp.raise_for_status()
        items = resp.json().get('items', [])
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items

def main():
    validators = fetch_all_validators()

    headers = [
        'Subnet Name', 'Score', 'Identity', 'Hotkey',
        'Total Stake Weight', 'VTrust', 'Dividends', 'Chk Take'
    ]
    rows = [headers]
    for v in validators:
        rows.append([
            v.get('subnetName') or v.get('subnet'),
            v.get('score'),
            v.get('identity'),
            v.get('hotkey'),
            v.get('totalStakeWeight'),
            v.get('vtrust'),
            v.get('dividends'),
            v.get('checkTake')
        ])

    sheet.clear()
    sheet.update(rows)
    print(f"Записано {len(rows)-1} строк в таблицу {spreadsheet_id}")

if __name__ == '__main__':
    main()
