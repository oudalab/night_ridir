from flask import Flask
from flask_restful import Api
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from resources.extract_phrases import PhraseExtractAPI

app = Flask(__name__)
api = Api(app)

api.add_resource(PhraseExtractAPI, '/get_phrases')

if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
