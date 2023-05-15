import os, pika, gridfs, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo_videos = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_videos.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if not err:
        return token
    return err


@server.route("/upload", methods=["POST"])
def upload():
    decoded_token, err = validate.validate_token(request)

    if err:
        return err

    decoded_token = json.loads(decoded_token)

    if not decoded_token["admin"]:
        return "Unauthorized", 401

    if len(request.files) != 1:
        return f"exactly one file required provided {len(request.files)}", 400

    for _, f in request.files.items():
        err = util.upload(f, fs_videos, channel, decoded_token)
        if err:
            return err
        return "success!", 200


@server.route("/download", methods=["GET"])
def download():
    decoded_token, err = validate.validate_token(request)

    if err:
        return err

    decoded_token = json.loads(decoded_token)

    if not decoded_token["admin"]:
        return "Unauthorized", 401

    mp3_fid = request.args.get("fid")

    if not mp3_fid:
        return "fid is required", 400

    try:
        mp3_file = fs_mp3s.get(ObjectId(mp3_fid))
        return send_file(mp3_file, download_name=f"{mp3_fid}.mp3")
    except Exception as err:
        return f"Either file does not exist or error getting the file {err}", 500


if __name__ == "__main__":
    server.run("0.0.0.0", port=8080)
