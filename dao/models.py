from minimongo import configure, Model
from minimongo.model import ObjectId
import utils
import time

"""
To Remove any Object from the Database Simply call object.remove()

"""
configure(database="bms")

class User(Model):
    @staticmethod
    def get_user_from_id(guid):
        return User.collection.find_one({'guid':guid})
    @staticmethod
    def update_user(update_dict):
        guid = update_dict["guid"]
        user = User.get_user_from_id(guid)
        if user:
            pass
        else:
            user = User(random = "axpr")
        for key in update_dict:
            #if key == "guid":
            #    continue
            user[key] = update_dict[key]
        return user.save()
    class Meta:
        database = "bms"
        collection = "user"

class Request(Model):
    #Rule only one user can open one active request at one time
    @staticmethod
    def get_request_from_user_id(guid):
        return Request.collection.find_one({'guid': guid, 'is_expired': False, 'is_matched': False})
    @staticmethod
    def create_request(update_dict):
        guid = update_dict["guid"]
        user = User.get_user_from_id(guid)
        request = Request({'guid': guid, 'is_expired': False, 'is_matched': False})
        for key in update_dict:
            if key == "guid":
                continue
            request[key] = update_dict[key]
        return request.save()
    class Meta:
        database = "bms"
        collection = "request"
