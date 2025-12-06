import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv('BOT_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')
