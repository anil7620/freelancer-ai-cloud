from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class Contract:
    collection = mongo.db.contracts

    @classmethod
    def find_one(cls, data):
        return cls.collection.find_one(data)
    

    @classmethod
    def insert_one(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)
    

    @classmethod
    def find(cls, data):
        # print(data)
        return list(cls.collection.find(data))

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
