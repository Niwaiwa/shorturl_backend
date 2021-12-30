from flask import Blueprint
from config import setting


api_v2 = Blueprint('v2', __name__, url_prefix='/v2')

@api_v2.route("/", methods=["GET"])
def hello_world_v2():
    from datetime import datetime
    return f"<p>Server running {setting.env_mode} time: {datetime.now(setting.sys_tz)} version: v{setting.version}, v2 test</p>"
