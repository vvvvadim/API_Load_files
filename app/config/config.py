import os
from dotenv import load_dotenv

load_dotenv()
CURRENT_URL = os.getenv("CURRENT_URL")
MEDIA_FOLDER = os.path.join('/'.join(os.getcwd().split('/')[:-1]), 'media')
DB_FOLDER = os.path.join('/'.join(os.getcwd().split('/')[:-1]), 'db')