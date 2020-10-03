from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from flask_cors import CORS

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
CORS(app)
jwt = JWTManager(app)
import modem_controller

if __name__ == '__main__':
    app.run(port='3333')
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(5001)
    # IOLoop.instance().start()