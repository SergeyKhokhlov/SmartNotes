# TG_TOKEN = "1363841624:AAEbh2XaTpf0wVK6nJaDTY6mxNs4gtpjTBY"
# TG_API_URL = None
import os

import sentry_sdk


# Путь до коренной папки `tele_bot`
BASE_PATH = os.path.dirname(os.path.dirname(__file__))

# вписать сюда токен от своего бота!!!
TG_TOKEN = "1363841624:AAEbh2XaTpf0wVK6nJaDTY6mxNs4gtpjTBY"

# На сервере не используем прокси-URL
TG_API_URL = None

# Sentry
# добавить свой DSN из https://sentry.io
sentry_sdk.init(
    dsn="dsn=https://4dd83f6842b04b4db2217119886364a6@o489213.ingest.sentry.io/5551048",
)
