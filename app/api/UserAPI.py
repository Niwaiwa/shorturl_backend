import logging
import traceback
from datetime import datetime
from config import setting
from common.Response import response
from common.cache.JWTAuth import JWTAuth
from crud.CRUDUser import CRUDUser
from flask import g, request
from pymongo.errors import PyMongoError
from pydantic import ValidationError
from schemas.User import UserUpdate, UserPassword


class UserAPI:
    logging = logging.getLogger(__name__)

    def delete_user(self):
        try:
            JWTAuth().del_token(g.user_id)
            _ = CRUDUser().delete_user(g.user_id)
            return response(0, http_code=204)
        except PyMongoError as e:
            UserAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)

    def get_user(self):
        try:
            user_info: dict = g.user_info
            user_last_login_utc: datetime = user_info['last_login']  # mongo client要打開tz_aware才會帶上tz, 未帶上tz則要主動處理setting.utc_tz.localize
            user_created_at_utc: datetime = user_info['_id'].generation_time  # generation_time 會帶上tz
            user_info['created_at'] = user_created_at_utc.astimezone(setting.sys_tz).isoformat(" ", "seconds")
            user_info['last_login'] = user_last_login_utc.astimezone(setting.sys_tz).isoformat(" ", "seconds")
            user_info.pop('_id', None)
            return response(0, data=user_info, http_code=200)
        except PyMongoError as e:
            UserAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)

    def update_user(self):
        try:
            data = request.get_json(silent=True)
            if data is None:
                return response(8, http_code=400)

            user_data = UserUpdate(**data)
            user_data_info = user_data.dict()
            UserAPI.logging.info(user_data_info)

            crud_user = CRUDUser()
            result = crud_user.update_user(g.user_id, user_data_info)
            UserAPI.logging.info(result)

            return response(0, http_code=200)
        except ValidationError as e:
            UserAPI.logging.info(e.json(indent=None))
            return response(8, http_code=400)
        except PyMongoError as e:
            UserAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)
