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
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(51), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False)
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
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    collections = db.relationship('Collection', backref='company', lazy='dynamic', cascade='all, delete-orphan', order_by='Collection.created_at')
    products = db.relationship('Product', backref='company', lazy='dynamic', cascade='all, delete-orphan', order_by='Product.code')

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
    __tablename__ = 'collection'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(64))
    products = db.relationship('Product', backref='collection', lazy='dynamic', cascade='all, delete-orphan', order_by='Product.code')

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
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    grid = db.Column(db.Unicode())
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(precision=20, scale=2), nullable=False, default=0)
    soldout = db.Column(db.Boolean(), default=False)
    image = db.Column(db.String(128))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'company': self.company.id,
            'collection': self.collection.id,
            'code': self.code,
            'name': self.name,
            'grid': self.grid,
            'quantity': self.quantity,
            'price': float(self.price),
            'image': self.image,
            'soldout': self.soldout,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __init__(self, data):
        self.name = data['name']
        self.code = data['code']
        self.name = data['name']
        self.grid = data['grid']
        self.quantity = int(data['quantity'])
        self.price = float(data['price'])

    def touch(self):
        self.updated_at = datetime.datetime.now(pytz.UTC)

    def update(self, data):
        self.name = data['name']
        self.code = data['code']
        self.name = data['name']
        self.grid = data['grid']
        self.quantity = int(data['quantity'])
        self.price = float(data['price'])
        self.touch()

class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2), nullable=False)
    name = db.Column(db.String(), nullable=False)
    cities = db.relationship('City', backref='state', lazy='dynamic', cascade='all, delete-orphan', order_by='City.name')

    def __init__(self, data):
        self.code = data['code']
        self.name = data['name']

    @property
    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }

class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    name = db.Column(db.String(), nullable=False)

    def __init__(self, name):
        self.name = name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))

    user = db.relationship('User', backref='customers')

    name = db.Column(db.String(), nullable=False)
    corporate_name = db.Column(db.String())
    cnpj = db.Column(db.String(14))
    ie = db.Column(db.String(9))

    city = db.relationship('City', backref='customers')
    address = db.Column(db.String())
    cep = db.Column(db.String())
    district = db.Column(db.String())
    number = db.Column(db.Integer)
    complement = db.Column(db.String())

    company_phone = db.Column(db.String())
    mobile_phone = db.Column(db.String())
    other_phone = db.Column(db.String())

    contact = db.Column(db.String())

    primary_email = db.Column(db.String())
    secondary_email = db.Column(db.String())

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, data):
        self.name = data['name']
        self.corporate_name = data['corporate_name']
        self.cnpj = data['cnpj']
        self.ie = data['ie']

        self.address = data['address']
        self.cep = data['cep']
        self.district = data['district']
        self.number = data['number']
        self.complement = data['complement']

        self.contact = data['contact']
        self.company_phone = data['company_phone']
        self.mobile_phone = data['mobile_phone']
        self.other_phone = data['other_phone']
        self.primary_email = data['primary_email']
        self.secondary_email = data['secondary_email']

    @property
    def serialize(self):
        return {
            'name': self.name,
            'corporate_name': self.corporate_name,
            'cnpj': self.cnpj,
            'ie': self.ie,
            'city': self.city.name if self.city else None,
            'address': self.address,
            'cep': self.cep,
            'district': self.district,
            'number': self.number,
            'complement': self.complement,
            'company_phone': self.company_phone,
            'mobile_phone': self.mobile_phone,
            'other_phone': self.other_phone,
            'contact': self.contact,
            'primary_email': self.primary_email,
            'secondary_email': self.secondary_email
        }

class OrderStatus(db.Model):
    __tablename__ = 'order_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.ForeignKey('order.id'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, data):
        return

class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    orderstatus_id = db.Column(db.Integer, db.ForeignKey('order_status.id'), nullable=False)

    user = db.relationship('User', backref='orders')
    orderstatus = db.relationship('OrderStatus', backref='orders')

    deliver = db.Column(db.String())
    payment = db.Column(db.String())
    d1 = db.Column(db.Numeric(precision=20, scale=2), default=0)
    d2 = db.Column(db.Numeric(precision=20, scale=2), default=0)
    d3 = db.Column(db.Numeric(precision=20, scale=2), default=0)
    d4 = db.Column(db.Numeric(precision=20, scale=2), default=0)

    freight = db.Column(db.String())
    shipping = db.Column(db.String())
    shipping_phone = db.Column(db.String())

    obs = db.Column(db.String())

    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan', order_by='OrderItem.created_at')

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
