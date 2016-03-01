import json

from flask import Flask
from flask import send_from_directory

from flask.ext.restful import Api

from models import db
from models import User

from resources import Authentication
from resources import Users
from resources import Companies
from resources import Collections
from resources import Products
from resources import Images

app = Flask(__name__)
app.config.from_object(__name__)

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import daemon

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'postgresql://jrs:jrs@localhost/jrs'
})

db.init_app(app)
api = Api(app)

api.add_resource(Authentication, '/authentication')
api.add_resource(Users, '/users', '/users/<int:id>')
api.add_resource(Companies, '/companies', '/companies/<int:id>')
api.add_resource(Collections, '/collections', '/collections/<int:id>')
api.add_resource(Products, '/products', '/products/<int:id>')
api.add_resource(Images, '/products/image')

@app.after_request
def after_reqeust(response):
    if 'WWW-Authenticate' in response.headers:
        del response.headers['WWW-Authenticate']
    return response

@app.route('/')
def send_template():
    return send_from_directory('templates', 'base.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/upload/<path:path>')
def send_upload(path):
    return send_from_directory('upload', path)

@app.cli.command()
def drop():
    db.drop_all()

@app.cli.command()
def create():
    db.create_all()

@app.cli.command()
def fill():
    u = User({'user': 'ramonsaraiva', 'password': '24810105ever', 'name': 'Ramon Saraiva', 'admin': True})
    db.session.add(u)
    db.session.commit()

@app.cli.command()
def tornado():
    log = open('tornado.log', 'a+')
    ctx = daemon.DaemonContext(stdout=log, stderr=log, working_directory='.')
    ctx.initgroups = False
    ctx.open()

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
