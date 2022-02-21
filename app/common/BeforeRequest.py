import logging
from flask import request, g
from common.Response import response
from common.cache.JWTAuth import JWTAuth
from config import setting
from crud.CRUDUser import CRUDUser


class BeforeRequest:
    def __init__(self):
        """
        Before all request handle
        """
        self.logging = logging.getLogger(__name__)
        self.logging.info('before_request')

        environ = request.headers.environ
        self.logging.info('Header')
        self.logging.debug(environ)
        self.request_path = environ['PATH_INFO']

    def handle(self):
        """
        Before all request handle
        若有其他需要處理的 加在此部分即可
        :return:
        """
        self.logging.info("handle")

        if self.request_path in setting.verify_path:
            return self._user_auth()
        return

    def _user_auth(self):
        """
        JWT Token 認證
        :return:
        """
        self.logging.info("_user_auth")

        auth_token: str = request.headers.get('Authorization', "")
        auth_token_split = auth_token.split(' ')
        if auth_token_split[0] != 'Bearer':
            return response(7, http_code=401)
        else:
            jwt_token = auth_token_split[1]

        self.logging.info(f'jwt_token: {jwt_token}')

        try:
            auth = JWTAuth().authenticate(jwt_token)  # 驗證 user_id 以及 token
        except Exception as e:
            logging.error(e)
            # Token 認證失敗 回傳http code 401
            return response(7, http_code=401)

        if auth:
            user_id = auth['user_id']
            user_info = CRUDUser().get_user_info_by_user_id(user_id)
            if user_info is None:
                return response(7, http_code=401)


            # user 資訊存入 global variable
            g.user_info = user_info
            g.user_id = user_id
            g.jwt_token = jwt_token
            g.admin = True if user_info.get('admin') else False
            return
        else:
            # Token 認證失敗 回傳http code 401
            return response(7, http_code=401)
