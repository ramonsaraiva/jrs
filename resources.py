import os
import datetime
import uuid

import pytz
import werkzeug
import magic

from flask import jsonify
from flask import abort
from flask import request
from flask import g

from flask.ext.restful import Resource
from flask.ext.restful import reqparse
from flask.ext.restful import abort

from sqlalchemy import func

from models import db
from models import User
from models import Company
from models import Collection
from models import Product

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'upload')

def get_format(filename):
    return filename.split('.')[1]

def get_mime(filename):
    mime = magic.Magic(mime=True)
    return mime.from_file('upload/products/{0}'.format(filename))

def requires_auth(f):
    def wrapper(*args, **kwargs):
        if not 'Authorization' in request.headers:
            abort(401)
        try:
            token = request.headers['Authorization'].split(' ')[1]
            user = User.query.filter(User.token == token).first()

            if not user:
                abort(401)
            g.user = user
        except:
            abort(401)

        return f(*args, **kwargs)
    return wrapper

def requires_admin(f):
    def wrapper(*args, **kwargs):
        if not g.user.admin:
            abort(401)
        return f(*args, **kwargs)
    return wrapper

class Authentication(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type=str, location='json', required=True)
        self.reqparse.add_argument('password', type=str, location='json', required=True)

    def post(self):
        args = self.reqparse.parse_args()
        user = User.query.filter(User.user == args['user'].lower()).first()

        if not user or not user.check_password(args['password']):
            abort(404)

        token = user.generate_token()
        db.session.commit()
        return jsonify({'token': token, 'user': user.serialize})

class Users(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type=str, location='json', required=True)
        self.reqparse.add_argument('name', type=str, location='json', required=True)
        self.reqparse.add_argument('admin', type=bool, location='json', required=False)

    @requires_auth
    @requires_admin
    def get(self, id=None):
        if not id:
            users = User.query.order_by(User.created_at).all()
            return jsonify(results=[u.serialize for u in users])
        user = User.query.get_or_404(id)
        return jsonify(user.serialize)

    @requires_auth
    @requires_admin
    def post(self):
        self.reqparse.add_argument('password', type=str, location='json', required=True)
        args = self.reqparse.parse_args()

        user = User(args)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize)

    @requires_auth
    @requires_admin
    def put(self, id):
        args = self.reqparse.parse_args()

        user = User.query.get_or_404(id)
        user.update(args)

        db.session.commit()
        return jsonify(user.serialize)

    @requires_auth
    @requires_admin
    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify(user.serialize)

class Companies(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json', required=True)

    @requires_auth
    def get(self, id=None):
        if not id:
            companies = Company.query.order_by(Company.created_at).all()
            return jsonify(results=[c.serialize for c in companies])
        company = Company.query.get_or_404(id)
        return jsonify(company.serialize)

    @requires_auth
    @requires_admin
    def post(self):
        args = self.reqparse.parse_args()

        company = Company(args)
        db.session.add(company)
        db.session.commit()
        return jsonify(company.serialize)

    @requires_auth
    @requires_admin
    def put(self, id):
        args = self.reqparse.parse_args()

        company = Company.query.get_or_404(id)
        company.update(args)

        db.session.commit()
        return jsonify(company.serialize)

    @requires_auth
    @requires_admin
    def delete(self, id):
        company = Company.query.get_or_404(id)
        db.session.delete(company)
        db.session.commit()
        return jsonify(company.serialize)

class Collections(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('company', type=int, location='json', required=True)
        self.reqparse.add_argument('name', type=unicode, location='json', required=True)

    @requires_auth
    def get(self, id=None):
        if not id:
            collections = Collection.query.order_by(Collection.company_id.asc()).all()
            return jsonify(results=[c.serialize for c in collections])
        collection = Collection.query.get_or_404(id)
        return jsonify(collection.serialize)

    @requires_auth
    @requires_admin
    def post(self):
        args = self.reqparse.parse_args()
        company = Company.query.get_or_404(args['company'])

        collection = Collection(args)
        collection.company = company

        db.session.add(collection)
        db.session.commit()
        return jsonify(collection.serialize)

    @requires_auth
    @requires_admin
    def put(self, id):
        args = self.reqparse.parse_args()
        collection = Collection.query.get_or_404(id)
        company = Company.query.get_or_404(args['company'])

        collection.update(args)
        collection.company = company

        db.session.commit()
        return jsonify(collection.serialize)

    @requires_auth
    @requires_admin
    def delete(self, id):
        collection = Collection.query.get_or_404(id)
        db.session.delete(collection)
        db.session.commit()
        return jsonify(collection.serialize)

class Products(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('company', type=int, location='json', required=True)
        self.reqparse.add_argument('collection', type=int, location='json', required=True)
        self.reqparse.add_argument('code', type=str, location='json', required=True)
        self.reqparse.add_argument('name', type=unicode, location='json', required=False)
        self.reqparse.add_argument('grid', type=unicode, location='json', required=False)
        self.reqparse.add_argument('quantity', type=str, location='json', required=True)
        self.reqparse.add_argument('price', type=str, location='json', required=True)
        self.reqparse.add_argument('image', type=str, location='json', required=False)

    @requires_auth
    def get(self, id=None):
        if not id:
            products = Product.query.order_by(Product.created_at.desc()).all()
            return jsonify(results=[p.serialize for p in products])
        product = Product.query.get_or_404(id)
        return jsonify(product.serialize)

    @requires_auth
    @requires_admin
    def post(self):
        args = self.reqparse.parse_args()
        company = Company.query.get_or_404(args['company'])
        collection = Collection.query.get_or_404(args['collection'])

        product = Product(args)
        product.company = company
        product.collection = collection

        db.session.add(product)
        db.session.flush()

        if 'image' in args:
            image = '{0}.{1}'.format(product.id, get_format(args['image']))
            os.rename(os.path.join(UPLOAD_FOLDER, 'tmp', args['image']), os.path.join(UPLOAD_FOLDER, 'products', image))
            product.image = image

        db.session.commit()
        return jsonify(product.serialize)

    @requires_auth
    @requires_admin
    def put(self, id):
        args = self.reqparse.parse_args()
        product = Product.query.get_or_404(id)
        company = Company.query.get_or_404(args['company'])
        collection = Collection.query.get_or_404(args['collection'])

        product.update(args)
        product.company = company
        product.collection = collection

        db.session.commit()
        return jsonify(product.serialize)

    @requires_auth
    @requires_admin
    def delete(self, id):
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify(product.serialize)

class Images(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True)

    @requires_auth
    @requires_admin
    def post(self):
        args = self.reqparse.parse_args()
        _file = args['file']

        temp = '{0}.{1}'.format(str(uuid.uuid4()), get_format(_file.filename))
        _file.save(os.path.join(UPLOAD_FOLDER, 'tmp', temp))
        return jsonify(temp=temp)
