import jwt, datetime, os
from flask import Flask, request
import mysql.connector

server = Flask(__name__)

# config
# server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")
db_config = {
    'user': os.environ.get("MYSQL_USER"),
    'password': os.environ.get("MYSQL_PASSWORD"),
    'host': os.environ.get("MYSQL_HOST"),
    'database': os.environ.get("MYSQL_DB"),
    'raise_on_warnings': True
}


@server.route("/login", methods=["POST"])
def login():
    print("login route called")
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    db_connection = mysql.connector.connect(**db_config)
    cursor = db_connection.cursor()

    cursor.execute("SELECT email, password FROM user WHERE email = %s", (auth.username, ))

    no_record = True

    for (username, password) in cursor:
        no_record = False
        print(username, password)
        if password != auth.password:
            return "username or password is incorrect", 401
        else:
            return create_jwt(auth.username, os.environ.get('JWT_SECRET'), True)

    if no_record:
        return "username or password is incorrect", 401

    db_connection.close()


def create_jwt(username, secret, authz):
    return jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(), # issued at
        "admin": authz
    }, secret, algorithm="HS256")


@server.route("/validate", methods=["POST"])
def validate_jwt():
    print("validate jwt route called")
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return "missing token", 401

    encoded_jwt = encoded_jwt.split(" ")[1]  # Bearer token

    print(encoded_jwt, os.environ.get("JWT_SECRET"))
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms="HS256")
    except:
        return "not authorized", 401

    return decoded, 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=3000)
