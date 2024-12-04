from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class JobPoster:
    collection = mongo.db.jobposters

    @classmethod
    def get_by_email(cls, email):
        return cls.collection.find_one({"email": email})
    

    @classmethod
    def find(cls, filter={}):
        return list(cls.collection.find(filter))
    

    @classmethod
    def count_documents(cls, filter={}):
        return cls.collection.count_documents(filter)


    @classmethod
    def exists_by_email(cls, email):
        return cls.collection.find_one({"email": email}) is not None
    
    @classmethod
    def find_one(cls, query):
        return cls.collection.find_one(query)

    @classmethod
    def find_all(cls):
        return list(cls.collection.find())

    @classmethod
    def find_by_id(cls, jobposter_id):
        return cls.collection.find_one({"_id": ObjectId(jobposter_id)})

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def count_all(cls):
        return cls.collection.count_documents({})

    @classmethod
    def delete(cls, jobposter_id):
        cls.collection.delete_one({"_id": ObjectId(jobposter_id)})

    @classmethod
    def update(cls, jobposter_id, data):
        cls.collection.update_one({"_id": ObjectId(jobposter_id)}, {"$set": data})

    @classmethod
    def find_by_jobposter_code(cls, jobposter_code):
        return cls.collection.find_one({"jobposter_code": jobposter_code})

    @classmethod
    def check_password(cls, user, password):
        return check_password_hash(user["password"], password)
