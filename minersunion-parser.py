import requests

SUMMARY_URL = 'https://api.minersunion.ai/metrics/summary/?format=json'
HISTORY_URL = 'https://api.minersunion.ai/metrics/history/?format=json'

def fetch_subnets(timeout=10):
    """Return list of all subnet objects (each containing 'netuid')."""
    r = requests.get(SUMMARY_URL, timeout=timeout)
    r.raise_for_status()
    payload = r.json()
    # Если API вернул список напрямую
    if isinstance(payload, list):
        return payload
    # Если API вернул объект с ключами data или validators
    if isinstance(payload, dict):
        data = payload.get('data')
        if isinstance(data, dict) and 'validators' in data:
            return data['validators']
        if 'validators' in payload:
            return payload['validators']
    return []

def fetch_history(netuid, timeout=10):
    """Fetch history for one subnet by netuid."""
    url = f"{HISTORY_URL}&netuid={netuid}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json().get('validators', [])

def main():
    subnets = fetch_subnets()
    total = len(subnets)
    print(f"Всего подсетей найдено: {total}")

    for sn in subnets:
        nid = sn.get('netuid')
        print(f"— Обрабатываем netuid={nid}")
        history = fetch_history(nid)
        print(f"   Записей в history: {len(history)}")
        # Здесь можно дальше обрабатывать sn и history…

if __name__ == '__main__':
    main()
