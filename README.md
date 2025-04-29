# MinersUnion Parser

Инструмент для автоматического сбора информации о валидаторах с сайта [Miners Union](https://app.minersunion.ai/validators) и загрузки её в Google Sheets.

---

## 📋 Содержание

- [Prerequisites](#prerequisites)
- [Установка](#installation)
- [Конфигурация](#configuration)
- [Запуск](#usage)
- [GitHub Secrets / CI](#github-secrets--ci)
- [Поддержка ".gitignore"](#gitignore)
- [Contributing](#contributing)

---

## Prerequisites

1. Python 3.8 или выше
2. pip (или другая система управления пакетами Python)
3. Аккаунт Google Cloud с включёнными API **Google Sheets** и **Google Drive**
4. Таблица Google Sheets, в которую будут записываться данные

---

## Установка

```bash
# Клонируем репозиторий
git clone https://github.com/scaleoka/minersunion-parser.git
cd minersunion-parser

# Рекомендуемо: создаём виртуальное окружение
python -m venv venv
# на Linux/macOS
source venv/bin/activate
# или на Windows
venv\Scripts\activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

---

## Configuration

Для корректной работы скрипта необходимо задать два обязательных параметра:

| Переменная окружения          | Описание                                                         |
|-------------------------------|------------------------------------------------------------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Путь к JSON-файлу сервисного аккаунта Google Cloud                |
| `SPREADSHEET_ID`              | ID Google Sheets (из URL таблицы: `https://docs.google.com/.../d/{ID}/...`) |

Пример на Linux/macOS (Bash):
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export SPREADSHEET_ID="1TuYcXnEM9sO0eo2XkecgmxCIsYB5dZDTQBPmCZBbw4o"
```

На Windows (PowerShell):
```powershell
setx GOOGLE_APPLICATION_CREDENTIALS "C:\path\to\credentials.json"
setx SPREADSHEET_ID "1TuYcXnEM9sO0eo2XkecgmxCIsYB5dZDTQBPmCZBbw4o"
```

Если вы используете GitHub Actions, добавьте эти секреты в Settings → Secrets:
- `GOOGLE_APPLICATION_CREDENTIALS` (содержимое JSON или путь в runner)
- `SPREADSHEET_ID`

---

## Запуск

```bash
python minersunion-parser.py
```

При успешном выполнении скрипта в консоли вы увидите сообщение о количестве записанных строк.

---

## GitHub Secrets / CI

При настройке CI (например, GitHub Actions) убедитесь, что в вашем workflow:
- находится шаг, устанавливающий Python
- задаёт переменные окружения `GOOGLE_APPLICATION_CREDENTIALS` и `SPREADSHEET_ID`
- копирует файл `credentials.json` (либо использует секреты)

Пример фрагмента workflow:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Write creds file
        run: |
          echo "$GOOGLE_APPLICATION_CREDENTIALS" > creds.json
      - name: Run parser
        env:
          GOOGLE_APPLICATION_CREDENTIALS: creds.json
          SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
        run: |
          python minersunion-parser.py
```

---

## .gitignore

```gitignore
# Python
__pycache__/
*.pyc

# Виртуальное окружение
venv/

# Секреты и креденшелы
*.json
.env
```

---

## Contributing

PR и issues приветствуются! Пожалуйста, опишите вашу идею и внесите изменения в соответствующие модули.

---

© 2025 MinersUnion Parser
