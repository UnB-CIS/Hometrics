import os
from urllib.parse import quote_plus

# Environment variables 
DB_USER = quote_plus(os.environ['MONGO_DB_USER'])
DB_PASSWORD = quote_plus(os.environ['MONGO_DB_PASS'])
DB_CLUSTER = 'cluster0.mhq2j'
DB_URI = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_CLUSTER}.mongodb.net/"


