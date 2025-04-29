import os
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Получение настроек из переменных окружения
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

if not SERVICE_ACCOUNT_FILE or not SPREADSHEET_ID:
    raise EnvironmentError(
        "Требуются переменные окружения GOOGLE_APPLICATION_CREDENTIALS и SPREADSHEET_ID"
    )

# Авторизация в Google Sheets
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_FILE, scope
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# Endpoint Miners Union API
API_URL = 'https://api.minersunion.ai/validators'

def fetch_all_validators(limit=1000):
    all_items = []
    page = 1
    while True:
        params = {'page': page, 'limit': limit}
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get('items', [])
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items


def main():
    validators = fetch_all_validators()

    # Заголовки для Google Sheets
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

    # Запись в Google Sheets
    sheet.clear()
    sheet.update(rows)

    print(f"Записано {len(rows)-1} строк в таблицу.")


if __name__ == '__main__':
    main()
