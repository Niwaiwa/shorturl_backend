from datetime import datetime
from database.MongoConn import MongoConn
from bson.objectid import ObjectId
from typing import Optional, Union
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

class CRUDKey:

    def __init__(self) -> None:
        self.coll = MongoConn().venus()['keys']

    def create_key(self, key: str) -> Union[str, None]:
        try:
            result = self.coll.insert_one({'key': key})
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            return None

    # def update_key(self, key: str, is_used: bool = False) -> Optional[dict]:
    #     result = self.coll.update_one({'key': key}, {"$set": {'is_used': is_used}})
    #     return result.raw_result

    def check_key_exist(self, key: str) -> bool:
        count = self.coll.count_documents({'key': key})
        return True if count > 0 else False
