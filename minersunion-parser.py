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
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
if not SERVICE_ACCOUNT_JSON or not SPREADSHEET_ID:
    logging.error("SERVICE_ACCOUNT_JSON or SPREADSHEET_ID not set")
    sys.exit(1)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(SERVICE_ACCOUNT_JSON),
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive']
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# Corrected API endpoints with JSON format parameter
SUMMARY_URL = 'https://api.minersunion.ai/metrics/summary/?format=json'
HISTORY_URL = 'https://api.minersunion.ai/metrics/history/?format=json'

def fetch_subnets(timeout=10):
    """Return list of all subnets (netuid, subnetName, etc.)"""
    r = requests.get(SUMMARY_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json().get('data', {}) or r.json()
    return data.get('validators', [])

def fetch_history(netuid, timeout=10):
    """Return list of validators from history for a given netuid"""
    url = f"{HISTORY_URL}&netuid={netuid}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json().get('validators', [])

def main():
    subnets = fetch_subnets()
    logging.info("Found subnets: %d", len(subnets))

    # Headers: summary fields + history fields
    headers = [
        'Subnet Name', 'Score Now', 'Identity', 'Hotkey',
        'Total Stake Weight', 'VTrust', 'Dividends', 'Chk Take',
        'UID', 'Score 7d', 'Score 24h', 'Tao Stake', 'Alpha Stake'
    ]
    rows = [headers]

    for sn in subnets:
        netuid = sn.get('netuid')
        name = sn.get('subnetName', '')
        score = sn.get('scoreNow', sn.get('score', ''))
        identity = sn.get('identity', '')
        hotkey = sn.get('hotkey', '')
        weight = sn.get('votingPower', '')
        vtrust = sn.get('vtrust', '')
        dividends = sn.get('dividends', '')
        chk_take = sn.get('checkTake', '')

        if netuid is None:
            logging.warning("Skipping subnet without netuid: %s", name)
            continue

        history = fetch_history(netuid)
        if not history:
            rows.append([name, score, identity, hotkey,
                         weight, vtrust, dividends, chk_take,
                         '', '', '', '', ''])
            continue

        for v in history:
            rows.append([
                name, score, identity, hotkey,
                weight, vtrust, dividends, chk_take,
                v.get('uid', ''),
                v.get('score7d', ''),
                v.get('score24h', ''),
                v.get('taoStake', ''),
                v.get('alphaStake', '')
            ])

    # Write to Google Sheets
    sheet.clear()
    sheet.update('A1', rows, value_input_option='RAW')
    logging.info("Done: wrote %d rows", len(rows) - 1)

if __name__ == '__main__':
    main()
