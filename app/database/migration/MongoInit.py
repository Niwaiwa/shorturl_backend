from database.MongoConn import MongoConn
from pymongo import IndexModel, ASCENDING, DESCENDING
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
admin_password = pwd_context.hash("password")

class MongoInit:
    collection_info = {
        'users': [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("api_key", ASCENDING)], unique=True),
        ],
        'keys': [
            IndexModel([("key", ASCENDING)], unique=True),
        ],
        'urls': [
            IndexModel([("key", ASCENDING)]),
            IndexModel([('user_id', ASCENDING)]),
        ]
    }

    def init_db_index(self, is_rebuild_index: bool = False):
        coll_name_list = MongoConn().venus().list_collection_names()
        for coll_name, indexes in self.collection_info.items():
            if coll_name not in coll_name_list:
                MongoConn().venus().create_collection(coll_name)
            if is_rebuild_index:
                MongoConn().venus()[coll_name].drop_indexes()
            MongoConn().venus()[coll_name].create_indexes(indexes)

        self.create_default_user()

    def create_default_user(self):
        admin_email = 'xxx@gmail.com'
        admin_user = MongoConn().venus()['users'].find_one({'email': admin_email})
        if admin_user is None:
            update_data = {'email': admin_email, 'password': admin_password, 'admin': True}
            MongoConn().venus()['users'].insert_one(update_data)



if __name__ == "__main__":
    MongoInit().init_db_index()
