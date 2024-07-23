from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
    send_from_directory,
)
import time
import calendar
from os import path, makedirs
from ..ext_database import Database

api = Blueprint("api", __name__, template_folder="templates", static_folder="static")

api_dir = path.abspath(path.dirname(__file__))
downloads_dir = path.join(api_dir, "downloads")
if not path.exists(downloads_dir):
    makedirs(downloads_dir)


def write_txt(filename, text, mode, encoding=None):
    with open(filename, mode, encoding=encoding) as txt_file:
        txt_file.write(text)


@api.route("/docs")
def docs():
    return render_template("api/index.html")


@api.route("/v1.0/db/queries", methods=["POST"])
def post_query():
    if not request.json or not "db" in request.json:
        response = {
            "status": "Invalid input",
            "error": "Некорретный входящий запрос",
        }
        return jsonify({"query": response}), 400
    if request.json["db"] == "vio":
        db_server = "DBP2P"
    elif request.json["db"] == "spu":
        db_server = "DBP1PROD"
    try:
        with Database(db_server, request.json["user"], request.json["password"]) as db:
            current_app.logger.info(f"query:\n{request.json['query']}")
            json_data = db.get_db_json_data(request.json["query"])
    except Exception as e:
        json_data = False
        app.logger.error(f"{repr(e)}")
        query = {"status": "Error", "error": f"{repr(e)}"}
        return jsonify({"query": query}), 400

    if json_data:
        ts = calendar.timegm(time.gmtime())
        download_filename_api = f"{ts}.json"
        base_url = request.base_url.rsplit("/", 4)[0]
        write_txt(
            path.join(downloads_dir, download_filename_api),
            json_data,
            "w",
            encoding="utf-8",
        )
        query = {
            "status": "Success",
            "url_file_result": f"{base_url}/api/downloads/{download_filename_api}",
        }
        return jsonify({"query": query}), 200


@api.route("/downloads/<path:download_filename_api>", methods=["GET", "POST"])
def downloads_api(download_filename_api):
    return send_from_directory(downloads_dir, download_filename_api)
