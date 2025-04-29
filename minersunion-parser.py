#!/usr/bin/env python3

import os
import sys
import json
import logging
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Google Sheets setup
SERVICE_ACCOUNT_JSON = os.environ.get('SERVICE_ACCOUNT_JSON')
SPREADSHEET_ID        = os.environ.get('SPREADSHEET_ID')
if not SERVICE_ACCOUNT_JSON or not SPREADSHEET_ID:
    logging.error("SERVICE_ACCOUNT_JSON or SPREADSHEET_ID not set")
    sys.exit(1)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(SERVICE_ACCOUNT_JSON),
    ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# API endpoints
SUMMARY_URL = 'https://api.minersunion.ai/metrics/summary/?format=json'
HISTORY_URL = 'https://api.minersunion.ai/metrics/history/?format=json'

def fetch_subnets(timeout=10):
    r = requests.get(SUMMARY_URL, timeout=timeout)
    r.raise_for_status()
    payload = r.json()
    if isinstance(payload, list):
        return payload
    data = payload.get('data') or payload
    return data.get('validators', []) if isinstance(data, dict) else []

def fetch_history(netuid, timeout=10):
    url = f"{HISTORY_URL}&netuid={netuid}"
    r   = requests.get(url, timeout=timeout)
    r.raise_for_status()
    payload = r.json()
    # Логируем для отладки
    logging.info("HISTORY payload for netuid=%s: %s", netuid, json.dumps(payload, indent=2))
    # Находим список валидаторов
    if isinstance(payload, dict):
        if 'validators' in payload and isinstance(payload['validators'], list):
            return payload['validators']
        data = payload.get('data')
        if isinstance(data, dict) and 'validators' in data and isinstance(data['validators'], list):
            return data['validators']
    elif isinstance(payload, list):
        return payload
    return []

def main():
    subnets = fetch_subnets()
    if not subnets:
        logging.error("No subnets found")
        sys.exit(1)

    mapping    = {int(sn['netuid']): sn.get('subnet_name','') for sn in subnets}
    max_netuid = max(mapping.keys())
    logging.info("Max netuid: %d", max_netuid)

    headers = [
        'netuid','subnet_name','uid','score_current','identity','hotkey',
        'total_stake','vtrust','dividends','chk_take',
    ]
    rows = [headers]

    for netuid in range(1, max_netuid+1):
        name    = mapping.get(netuid, '')
        logging.info("Processing netuid=%d (%s)", netuid, name)
        history = fetch_history(netuid)
        if not history:
            rows.append([netuid, name] + ['']*(len(headers)-2))
            continue

        # Отладка: вывести ключи первого валидатора
        logging.info("Validator keys for netuid=%d: %s", netuid, list(history[0].keys()))

        for v in history:
            m = v.get('metrics', {})

            total_stake = m.get('total_stake', '')
            vtrust      = m.get('vtrust', '')
            dividends   = m.get('dividends', '')
            chk_take    = m.get('chk_take', '')

            rows.append([
                netuid,
                name,
                v.get('uid',''),
                v.get('score_current',''),
                v.get('identity',''),
                v.get('hotkey',''),
                total_stake,
                vtrust,
                dividends,
                chk_take,
            ])

    sheet.clear()
    sheet.update('A1', rows, value_input_option='RAW')
    logging.info("Done. Rows written (excl. header): %d", len(rows)-1)

if __name__ == "__main__":
    main()
