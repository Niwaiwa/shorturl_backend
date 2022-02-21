import logging
import traceback
from common.Response import response
from common.ReturnCode import ReturnError
from crud.CRUDKey import CRUDKey
from flask import g, request, redirect
from pymongo.errors import PyMongoError
from pydantic import ValidationError
from redis.exceptions import RedisError
from schemas.Key import KeyDelete


class KeyAPI:
    logging = logging.getLogger(__name__)

    def delete_key(self):
        try:
            if not g.admin: response(7, http_code=400)

            data = request.get_json(silent=True)
            if data is None:
                return response(2, http_code=400)

            key_data = KeyDelete(**data)
            key = key_data.key
            crud_key = CRUDKey()
            del_key_result = crud_key.delete_key(key)
            if del_key_result is None: return response(14, http_code=200)

            return response(0, http_code=200)
        except ValidationError as e:
            KeyAPI.logging.info(e.json(indent=None))
            return response(8, http_code=400)
        except RedisError as e:
            KeyAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(4, http_code=503)
        except PyMongoError as e:
            KeyAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)
