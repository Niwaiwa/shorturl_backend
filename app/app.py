import logging
import json
import os
import traceback
from flask import Flask, abort, jsonify, send_from_directory, g
from config import setting
from config.logging import RequestFormatter
from common.Response import response
from common.BeforeRequest import BeforeRequest
from api.AuthAPI import AuthAPI
from api.UserAPI import UserAPI
from api.UrlAPI import UrlAPI
from api_v2 import api_v2
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException

formatter = RequestFormatter(
    '[%(uuid)s] - %(asctime)s - (%(process)d-%(thread)d-%(lineno)d) - %(name)s - [%(levelname)s] - %(message)s'
)

sh = logging.StreamHandler()
sh.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(sh)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.register_blueprint(api_v2)

app.add_url_rule('/login', view_func=AuthAPI().login, methods=('POST',))
app.add_url_rule('/logout', view_func=AuthAPI().logout, methods=('POST',))
app.add_url_rule('/register', view_func=AuthAPI().register, methods=('POST',))
app.add_url_rule('/user', view_func=UserAPI().delete_user, methods=('DELETE',))
app.add_url_rule('/user', view_func=UserAPI().get_user, methods=('GET',))
app.add_url_rule('/user', view_func=UserAPI().update_user, methods=('POST',))
app.add_url_rule('/url', view_func=UrlAPI().create_url, methods=('POST',))
app.add_url_rule('/url', view_func=UrlAPI().delete_url, methods=('DELETE',))
app.add_url_rule('/<key>', view_func=UrlAPI().forward_url, methods=('GET',))

# public
# TODO: implement rate limit
app.add_url_rule('/create', view_func=UrlAPI().create_url_public, methods=('POST',))

@app.route("/", methods=["GET"])
def hello_world():
    from datetime import datetime
    return f"<p>Server running {setting.env_mode} time: {datetime.now(setting.sys_tz)} version: v{setting.version}</p>"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.before_request
def before_request():
    return BeforeRequest().handle()

# @app.after_request
# def after_request(response):
#     response.headers['SU-RequestId'] = g.uuid
#     return response

# @app.teardown_request
# def teardown_request(exception=None):
#     if exception:
#         logging.error(exception)
#     request_path = request.headers.environ['PATH_INFO']
#     if request_path in setting.VerifyExceptionPaths[:3]:
#         return
#     TeardownRequest().audit_log()

@app.errorhandler(Exception)
def catch_exception(e):
    logger.error(traceback.format_exc().replace("\n", ""))
    if isinstance(e, HTTPException):
        e_resp = e.get_response()
        # replace the body with JSON
        e_resp.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        e_resp.content_type = "application/json"
        return e_resp # or return e for html

    return response(1, 'server error', http_code=500)


if __name__ == "__main__":
    # from database.migration.MongoInit import MongoInit
    # MongoInit().init_db_index()
    app.run('0.0.0.0', 8000)
