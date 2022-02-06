from bson.objectid import ObjectId
from datetime import datetime
from database.MongoConn import MongoConn
from pymongo import DESCENDING
from typing import Optional


class CRUDUrl:

    def __init__(self) -> None:
        self.coll = MongoConn().venus()['urls']

    def create_url(self, key: str, origin_url: str, user_id: str = None) -> str:
        data = {'key': key, 'origin_url': origin_url}
        if user_id: data.update({'user_id': user_id})
        result = self.coll.insert_one(data)
        return str(result.inserted_id)

    def update_url(self, key: str, expired_at: datetime) -> Optional[dict]:
        result = self.coll.update_one({'key': key}, {"$set": {'expired_at': expired_at}})
        return result.raw_result

    def delete_url(self, key: str, user_id: str = None) -> str:
        filter = {'key': key}
        if user_id: filter.update({'user_id': user_id})
        result = self.coll.find_one_and_delete(filter)
        return result

    def get_url(self, key: str):
        return self.coll.find_one({key: key})

    def get_urls(self, user_id: str = None, page: int = 0, count: int = 10):
        data = {}
        if user_id: data.update({'user_id': ObjectId(user_id)})
        return self.coll.find(data, skip=page*count, limit=count, sort=[('_id', DESCENDING)])
