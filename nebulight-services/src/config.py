from dotenv import load_dotenv
import os

load_dotenv()

DB_PASSWORD= os.getenv('DB_PASSWORD')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

