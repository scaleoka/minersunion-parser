import os
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Читаем сервис-аккаунт как raw JSON из переменных окружения
sa_json = os.environ.get('SERVICE_ACCOUNT_JSON')
if not sa_json:
    raise EnvironmentError("SERVICE_ACCOUNT_JSON не задана в переменных окружения")

# Парсим JSON прямо из строки
sa_info = json.loads(sa_json)

# Читаем ID Google Sheets
spreadsheet_id = os.environ.get('SPREADSHEET_ID')
if not spreadsheet_id:
    raise EnvironmentError("SPREADSHEET_ID не задана в переменных окружения")

# Авторизация в Google Sheets
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(spreadsheet_id).sheet1

def fetch_all_validators():
    """Получаем весь массив метрик валидаторов одним запросом."""
    url = 'https://api.minersunion.ai/metrics/summary/'
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def main():
    validators = fetch_all_validators()

    # Заголовки для Google Sheets
    headers = [
        'Subnet Name', 'Score', 'Identity', 'Hotkey',
        'Total Stake Weight', 'VTrust', 'Dividends', 'Chk Take'
    ]
    rows = [headers]

    # Собираем строки из полученных данных
    for v in validators:
        rows.append([
            v.get('subnetName'),
            v.get('score'),
            v.get('identity'),
            v.get('hotkey'),
            v.get('votingPower'),
            v.get('vtrust'),
            v.get('dividends'),
            v.get('checkTake'),
        ])

    # Записываем в Google Sheets
    sheet.clear()
    sheet.update(rows)
    print(f"Записано {len(rows)-1} строк в таблицу {spreadsheet_id}")

if __name__ == '__main__':
    main()
