import os
import random
import datetime
import time
import json
import hashlib
import binascii

import pytz

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(128))
    password = db.Column(db.String(51))
    name = db.Column(db.String(64))
    admin = db.Column(db.Boolean())
    token = db.Column(db.String(30))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user': self.user,
            'name': self.name,
            'admin': self.admin,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __init__(self, data):
        self.user = data['user'].lower()
        self.set_password(data['password'])
        self.name = data['name']
        self.admin = data['admin'] if 'admin' in data else False

    def set_password(self, raw_password):
        algo = 'sha1'
        salt = hashlib.sha1('{0}{1}'.format(str(random.random()), str(random.random()))).hexdigest()[:5]
        hsh = hashlib.sha1('{0}{1}'.format(salt, raw_password)).hexdigest()
        self.password = '{0}${1}${2}'.format(algo, salt, hsh)

    def check_password(self, raw_password):
        algo, salt, hsh = self.password.split('$')
        return hsh == hashlib.sha1('{0}{1}'.format(salt, raw_password)).hexdigest()

    def generate_token(self):
        self.token = binascii.b2a_hex(os.urandom(15))
        return self.token

    def touch(self):
        self.updated_at = datetime.datetime.now(pytz.UTC)

    def update(self, data):
        self.user = data['user'].lower()
        self.name = data['name']
        self.touch()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    collections = db.relationship('Collection', backref='company', lazy='dynamic', cascade='all, delete-orphan', order_by='Collection.created_at')

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __init__(self, data):
        self.name = data['name']

    def touch(self):
        self.updated_at = datetime.datetime.now(pytz.UTC)

    def update(self, data):
        self.name = data['name']
        self.touch()

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(64))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'company': self.company_id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __init__(self, data):
        self.name = data['name']

    def touch(self):
        self.updated_at = datetime.datetime.now(pytz.UTC)

    def update(self, data):
        self.name = data['name']
        self.touch()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.String(16))
    name = db.Column(db.String(64))
    grid = db.Column(db.Unicode())
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(precision=20, scale=0), default=0)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'collection_id': self.company_id,
            'code': self.code,
            'name': self.name,
            'grid': self.grid,
            'quantity': self.quantity,
            'price': float(self.price),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __init__(self, data):
        self.name = data['name']
        self.company = Company.query.get_or_404(data['company'])
        self.collection = Company.query.get_or_404(data['collection'])
        self.code = data['code']
        self.name = data['name']
        self.grid = data['grid']
        self.quantity = data['quantity']
        self.price = data['price']

    def touch(self):
        self.updated_at = datetime.datetime.now(pytz.UTC)

    def update(self, data):
        self.name = data['name']
        self.company = Company.query.get_or_404(data['company'])
        self.collection = Company.query.get_or_404(data['collection'])
        self.code = data['code']
        self.name = data['name']
        self.grid = data['grid']
        self.quantity = data['quantity']
        self.price = data['price']
        self.touch()
