# hostbot/serve.py
from bottle import route, run
from json import dumps
from datetime import datetime
from socket import gethostname


@route("/")
def index():
    result = {}
    result["time"] = datetime.now().isoformat()
    # ホスト名(localhostではない)を取得し、resultのキーhostに格納する
    result["host"] = gethostname()
    return dumps(result)

if __name__ == "__main__":
    run(host="0.0.0.0", port=80)




