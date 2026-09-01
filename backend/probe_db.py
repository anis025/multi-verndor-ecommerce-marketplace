import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient
c = MongoClient(os.environ.get('MONGODB_URL', 'mongodb://localhost:27017'))
print('databases:', c.list_database_names())
for d in ['hatify_db', 'hatify']:
    try:
        cnt = c[d].users.count_documents({'role': 'admin'})
        print(f'  {d}: admin users =', cnt)
    except Exception as e:
        print(f'  {d}: err', e)
