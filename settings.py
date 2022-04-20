from dotenv import load_dotenv
from os import getenv

load_dotenv()
# Get token
API_TOKEN = getenv('tgbot_token')

HOSP_HOST = getenv('hosp_mysql_host')
HOSP_PORT = getenv('hosp_mysql_port')
HOSP_USER = getenv('hosp_mysql_user')
HOSP_PASS = getenv('hosp_mysql_password')
HOSP_DB = getenv('hosp_mysql_database')

BOT_HOST = getenv('bot_mysql_host')
BOT_PORT = getenv('bot_mysql_port')
BOT_USER = getenv('bot_mysql_user')
BOT_PASS = getenv('bot_mysql_password')
BOT_DB = getenv('bot_mysql_database')
