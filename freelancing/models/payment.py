from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId


class Payment:
    collection = mongo.db.payments

    @classmethod
    def find_all(cls):
        return list(cls.collection.find())
    

    @classmethod
    def count_documents(cls, filter={}):
        return cls.collection.count_documents(filter)
    
    @classmethod
    def find(cls, filter={}):
        return list(cls.collection.find(filter))
    

    @classmethod
    def insert_one(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def create(cls, data):
        try:
            cls.collection.insert_one(data)
            return True
        except Exception as e:
            raise e


    @classmethod
    def aggregate(cls, pipeline):
        return cls.collection.aggregate(pipeline)