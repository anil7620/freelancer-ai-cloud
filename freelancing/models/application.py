from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class Application:
    collection = mongo.db.applications

    @classmethod
    def find_one(cls, data):
        return cls.collection.find_one(data)
    

    @classmethod
    def append_comment(cls, application_id, comment):
        cls.collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$push": {"comments": comment}}  # Use `$push` to add to the array
        )    

    @classmethod
    def update_comments(cls, application_id, comments):
        cls.collection.update_one({"_id": ObjectId(application_id)}, {"$set": {"comments": comments}})
    

    @classmethod
    def insert_one(cls, data):
        return cls.collection.insert_one(data)
    

    @classmethod
    def count_by_jobposter(cls, jobposter_id):
        """
        Count applications by job poster.
        """
        return cls.collection.count_documents({"jobposter_id": ObjectId(jobposter_id)})
    

    @classmethod
    def find(cls, data):
        return list(cls.collection.find(data))
    

    @classmethod
    def count_documents(cls, filter={}):
        """
        Count documents in the projects collection.
        """
        return cls.collection.count_documents(filter)

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def find_by_employee_id(cls, employee_id):
        return cls.collection.find_one({"employee_id": ObjectId(employee_id)})

    @classmethod
    def find_by_contract_id(cls, contract_id):
        return cls.collection.find_one({"_id": ObjectId(contract_id)})

    @classmethod
    def find_all(cls):
        return list(cls.collection.find())

    @classmethod
    def update(cls, contract_id, data):
        cls.collection.update_one({"_id": ObjectId(contract_id)}, {"$set": data})

    @classmethod
    def update_schedule(cls, contract_id, start_time, end_time):
        cls.collection.update_one(
            {"_id": ObjectId(contract_id)},
            {"$set": {"start_time": start_time, "end_time": end_time}},
        )

    @classmethod
    def delete(cls, contract_id):
        cls.collection.delete_one({"_id": ObjectId(contract_id)})
