from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class Project:
    collection = mongo.db.projects

    @classmethod
    def find_one(cls, data):
        return cls.collection.find_one(data)
    

    @classmethod
    def update_status(cls, project_id, status):
        cls.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"status": status}},
        )
    

    @classmethod
    def find_by_jobposter(cls, jobposter_id):
        jobs = cls.collection.find({"jobposter_id": ObjectId(jobposter_id)})
        # print(jobs)
        return jobs
    

    @classmethod
    def find(cls, data):
        return list(cls.collection.find(data))
    

    @classmethod
    def insert_one(cls, data):
        return cls.collection.insert_one(data)
    

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
    def update(cls, project_id, data):
        cls.collection.update_one({"_id": ObjectId(project_id)}, {"$set": data})


    @classmethod
    def update_schedule(cls, contract_id, start_time, end_time):
        cls.collection.update_one(
            {"_id": ObjectId(contract_id)},
            {"$set": {"start_time": start_time, "end_time": end_time}},
        )

    @classmethod
    def delete(cls, contract_id):
        cls.collection.delete_one({"_id": ObjectId(contract_id)})
