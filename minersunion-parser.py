import os
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Чтение параметров из переменных окружения
# SERVICE_ACCOUNT_JSON может быть либо путём к JSON-файлу, либо строкой с самим JSON
sa_env = os.environ.get('SERVICE_ACCOUNT_JSON')
if not sa_env:
    raise EnvironmentError("Переменная окружения SERVICE_ACCOUNT_JSON не задана")

spreadsheet_id = os.environ.get('SPREADSHEET_ID')
if not spreadsheet_id:
    raise EnvironmentError("Переменная окружения SPREADSHEET_ID не задана")

# Определяем, что содержится в SERVICE_ACCOUNT_JSON
if sa_env.strip().startswith('{'):
    # получен raw JSON
    sa_info = json.loads(sa_env)
else:
    # интерпретируем как путь к файлу
    with open(sa_env, 'r', encoding='utf-8') as f:
        sa_info = json.load(f)

# Авторизация в Google Sheets через сервисный аккаунт
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(spreadsheet_id).sheet1

# Fetching validators from Miners Union API
def fetch_all_validators(limit=1000):
    all_items = []
    page = 1
    while True:
        params = {'page': page, 'limit': limit}
        resp = requests.get('https://api.minersunion.ai/validators', params=params)
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

    # Сборка строк для записи
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
    print(f"Записано {len(rows)-1} строк в таблицу {spreadsheet_id}")


if __name__ == '__main__':
    main()
