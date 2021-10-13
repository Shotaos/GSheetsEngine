from pathlib import Path

GOOGLE_APP_CONFIG = {"web": {"client_id": "693899014701-h1f14417n5h0rp253l690q7nklnc26pe.apps.googleusercontent.com", "project_id": "sanguine-robot-258318", "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                             "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_secret": "t694D08nSpGhrMqpBO3bwiK1"}}

SETTINGS_DIR= Path.home() / ".sheetsearch"
SETTINGS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = SETTINGS_DIR / 'settingsv2.json'
TOKEN_FILE = SETTINGS_DIR / 'token.json'
TOPICS_FILE = SETTINGS_DIR / 'topics.json'
ASSETS_CACHE = SETTINGS_DIR / 'assets'
ICONS_CACHE = SETTINGS_DIR / 'icons'
ASSETS_CACHE.mkdir(exist_ok=True)
ICONS_CACHE.mkdir(exist_ok=True)
