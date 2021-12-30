from datetime import datetime
from database.MongoConn import MongoConn
from bson.objectid import ObjectId
from typing import Optional
from pymongo import ReturnDocument


class CRUDKey:

    def __init__(self) -> None:
        self.coll = MongoConn().venus()['keys']

    def create_key(self, key: str, is_used: bool = True) -> str:
        filter = {'key': key, 'is_used': False}
        update = {'$set': {'key': key, 'is_used': True}}
        result = self.coll.find_one_and_update(filter, update, upsert=True, return_document=ReturnDocument.AFTER)
        return result
        # result = self.coll.insert_one({'key': key, 'is_used': is_used})
        # return str(result.inserted_id)

    def update_key(self, key: str, is_used: bool = False) -> Optional[dict]:
        result = self.coll.update_one({'key': key}, {"$set": {'is_used': is_used}})
        return result.raw_result
