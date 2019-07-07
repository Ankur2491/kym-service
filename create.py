from pymongo import MongoClient
client = MongoClient('localhost:27017',username='root',password='ATIhH2s9gqpc')
db=client.admin
newCol=db["ratings"]
newFile= {}
x=newCol.insert_one(newFile)
