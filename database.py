import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError
from datetime import datetime
load_dotenv()  # Load environment variables from .env file

class Database:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri:
            raise ValueError("No MongoDB URI found in environment variables")
        self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        self.db = self.client.get_database('Information_Retrival_News')  # Explicitly specify the database name

    def get_collection(self, collection_name):
        return self.db[collection_name]

    

# Example usage:
# db_instance = Database()
# response = db_instance.get_collection('news').insert_one({
#     'title': 'Hello, world!',
#     'content': 'This is a test document.',
#     'date': datetime.now()
# })
# print(response)

# {
#     "_id": "https://ithelp.ithome.com.tw/articles/10327108",  // 唯一 ID
#     "title": "【Day 1】Python 爬蟲入門",
#     "link": "https://ithelp.ithome.com.tw/articles/10327108",
#     "content": "本文將介紹如何使用 Python 進行網頁爬蟲...",
#     "date": "2025-03-23T12:00:00"  // 爬取時間
# }