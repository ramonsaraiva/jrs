import datetime
import pytz

from flask import jsonify
from flask import abort
from flask import request
from flask import g

from flask.ext.restful import Resource
from flask.ext.restful import reqparse
from flask.ext.restful import abort

from models import db
from models import User
from models import Company
from models import Collection

from sqlalchemy import func

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
        self.reqparse.add_argument('name', type=str, location='json', required=True)

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
        print(request.data)
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
