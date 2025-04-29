import os
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 1) Читаем JSON сервис-аккаунта из переменных окружения
sa_json = os.environ.get('SERVICE_ACCOUNT_JSON')
if not sa_json:
    raise EnvironmentError("SERVICE_ACCOUNT_JSON не задана в переменных окружения")

# 2) Парсим его сразу из строки
sa_info = json.loads(sa_json)

# 3) Читаем ID Google Sheets
spreadsheet_id = os.environ.get('SPREADSHEET_ID')
if not spreadsheet_id:
    raise EnvironmentError("SPREADSHEET_ID не задана в переменных окружения")

# 4) Авторизуемся в Google Sheets
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(spreadsheet_id).sheet1

def fetch_all_validators():
    """
    Достаём сразу весь массив валидаторов по endpoint /metrics/summary/
    (в нём есть все нужные поля, без пагинации).
    """
    url = 'https://api.minersunion.ai/metrics/summary/'
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def main():
    validators = fetch_all_validators()

    # Заголовки колонок
    headers = [
        'Subnet Name', 'Score', 'Identity', 'Hotkey',
        'Total Stake Weight', 'VTrust', 'Dividends', 'Chk Take'
    ]
    rows = [headers]

    # Собираем данные
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

    # Пишем в Google Sheets
    sheet.clear()
    sheet.update(rows)
    print(f"Записано {len(rows)-1} строк в таблицу {spreadsheet_id}")

if __name__ == '__main__':
    main()
