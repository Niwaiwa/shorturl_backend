import logging
import traceback
from datetime import datetime
from config import setting
from common.Response import response
from common.ReturnCode import ReturnError
from common.cache.JWTAuth import JWTAuth
from crud.CRUDUrl import CRUDUrl
from crud.CRUDKey import CRUDKey
from flask import g, request, redirect
from pymongo.errors import PyMongoError
from pydantic import ValidationError
from redis.exceptions import RedisError
from schemas.Url import UrlCreate, UrlDelete, UrlGet
from utils.Base64Key import Base64Key


class UrlAPI:
    logging = logging.getLogger(__name__)

    def forward_url(self, key: str):
        try:
            logging.info(key)
            crud_url = CRUDUrl()
            url_info = crud_url.get_url(key)
            if url_info is None: return response(13, http_code=404)
            return redirect(url_info['origin_url'])
        except RedisError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(4, http_code=503)
        except PyMongoError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)

    def create_url(self):
        try:
            data = request.get_json(silent=True)
            if data is None:
                return response(2, http_code=400)

            url_data = UrlCreate(**data)
            key = self._create_key(url_data.key)

            crud_url = CRUDUrl()
            result = crud_url.create_url(key, url_data.origin_url, g.user_id)

            response_data = {
                'domain': setting.api_domain,
                'key': key,
            }
            return response(0, data=response_data, http_code=201)
        except ValidationError as e:
            UrlAPI.logging.info(e.json(indent=None))
            return response(8, http_code=400)
        except RedisError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(4, http_code=503)
        except PyMongoError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)

    def create_url_public(self):
        try:
            data = request.get_json(silent=True)
            if data is None:
                return response(2, http_code=400)

            url_data = UrlCreate(**data)
            key = self._create_key(url_data.key)

            crud_url = CRUDUrl()
            result = crud_url.create_url(key, url_data.origin_url)
            response_data = {
                'domain': setting.api_domain,
                'key': key,
            }
            return response(0, data=response_data, http_code=201)
        except ValidationError as e:
            UrlAPI.logging.info(e.json(indent=None))
            return response(8, http_code=400)
        except ReturnError as e:
            UrlAPI.logging.info(e.message)
            return response(e.code, http_code=e.http_code)
        except RedisError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(4, http_code=503)
        except PyMongoError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)

    def _create_key(self, url_data_key) -> str:
        crud_key = CRUDKey()
        if url_data_key:
            key = url_data_key
            result = crud_key.create_key(key)
            if result is None: raise ReturnError(10, http_code=200)
        else:
            try_num = 1
            key = Base64Key().gen_key()
            while True:
                result = crud_key.create_key(key)
                if result is None:
                    key = Base64Key().gen_key()
                    if try_num >= 5: raise ReturnError(10, http_code=200)
                    try_num += 1
                    continue
                else:
                    break
        return key

    def delete_url(self):
        try:
            data = request.get_json(silent=True)
            if data is None:
                return response(2, http_code=400)

            url_data = UrlDelete(**data)
            key = url_data.key
            user_id = None if g.admin else g.user_id
            crud_url = CRUDUrl()
            del_url_result = crud_url.delete_url(key, user_id)
            if del_url_result is None: return response(12, http_code=200)

            return response(0, http_code=200)
        except ValidationError as e:
            UrlAPI.logging.info(e.json(indent=None))
            return response(8, http_code=400)
        except RedisError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(4, http_code=503)
        except PyMongoError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)

    def get_url(self):
        try:
            data = request.get_json(silent=True)
            if data is None:
                return response(2, http_code=400)

            crud_url = CRUDUrl()
            if g.admin:
                UrlAPI.logging.info('admin')
                get_data = UrlGet(**data)
                urls: list = crud_url.get_urls(None, get_data.page - 1, get_data.count)
            else:
                urls: list = crud_url.get_urls(g.user_id)

            response_data = {
                'list': urls,
            }
            return response(0, data=response_data, http_code=200)
        except ValidationError as e:
            UrlAPI.logging.info(e.json(indent=None))
            return response(8, http_code=400)
        except PyMongoError as e:
            UrlAPI.logging.error(traceback.format_exc().replace("\n", ""))
            return response(1, http_code=503)