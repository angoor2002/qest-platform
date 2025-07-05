# app.py
import os
from dotenv import load_dotenv   # pip install python-dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()                    # loads .env into environment
uri = os.environ["MONGODB_URI"]

client = MongoClient(uri, server_api=ServerApi('1'))
# db = client["myDB"]              # create/use db
# people = db["people"]            # create/use collection

db=client['db1']

document={"name":"Ankur","city":"Hyderabad"}

people_collection = db["people"]         # or db.people
insert_doc = people_collection.insert_one(document)

# # INSERT -------------------------------------------------
# doc_id = people.insert_one({"name": "Grace", "age": 33}).inserted_id
# print("inserted:", doc_id)

# # FIND ONE ----------------------------------------------
# grace = people.find_one({"name": "Grace"})
# print("found:", grace)

# # FIND MANY ---------------------------------------------
# for p in people.find({"age": {"$gte": 30}}):
#     print(p)

# # UPDATE -------------------------------------------------
# people.update_one({"name": "Grace"},
#                   {"$set": {"age": 34}})

# # DELETE -------------------------------------------------
# people.delete_one({"name": "Grace"})
