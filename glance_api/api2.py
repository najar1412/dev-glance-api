import sqlite3
import uuid

from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import settings
from modules import convert
from modules import models
from modules import functions

# Config
# init app and db
app = Flask(__name__)
# conn = sqlite3.connect('example.db')

# config
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_DATABASE
engine = create_engine(settings.POSTGRES_DATABASE, echo=False)
api = Api(app, '/glance/v2')
# db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Init sessionmaker
Session = sessionmaker(bind=engine)

"""
'''development tools'''
# functions
session = Session()
functions.__reset_db(session, engine)
"""

# helpers
def resp(status=None, data=None, link=None, error=None, message=None):
    """Function im using to build responses"""
    response = {
        'status': status, 'data': data, 'link': link,
        'error': error, 'message': message
    }

    remove_none = []

    for x in response:
        if response[x] == None:
            remove_none.append(x)

    for x in remove_none:
        del response[x]

    return response

# auth
# Basic HTTP auth
@auth.verify_password
def verify(username, password):
    account_details = {'username': username, 'password': password}

    session = Session()
    validate_account = functions.get_account(session, **account_details)
    session.close()

    return validate_account


# API resources
class Entry(Resource):
    @auth.login_required
    def get(self):
        entry = {
            'name': 'gallery api',
            'version': 'v2',
            'resources': ''
        }

        return entry, 200


class Accounts(Resource):
    @auth.login_required
    def get(self, id):
        session = Session()
        raw_account = session.query(models.Account).filter_by(id=id).first()
        session.close()

        response = resp(status='success', data=convert.jsonify((raw_account,)))
        return response, 200


    @auth.login_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('galleries', type=str, help='help text')
        args = parser.parse_args()

        raw_account = models.Account.query.filter_by(id=id).first()

        if raw_account != None:
            if 'galleries' in args and args['galleries'] != None:
                raw_gallery = Gallery.query.filter_by(id=args['galleries']).first()

                if raw_gallery != None:
                    raw_account.galleries.append(raw_gallery)
                    db.session.commit()

                    response = resp(
                        status='success', link='/accounts/{}'.format(raw_account.id)
                        ), 201

                    return response

                else:
                    return resp(error='no such gallery id')

            else:
                return resp(error='must enter gallery id')

        else:
            return resp(error='no such account id')


    @auth.login_required
    def delete(self, id):
        session = Session()
        raw_account = session.query(models.Account).filter_by(id=id).first()

        if auth.username() == raw_account.username:
            session.delete(raw_account)
            session.commit()

            response = resp(status='success', message='account successfully deleted')

            session.close()
            return response

        else:
            session.close()
            return resp(message='Account can only be if logged in as the same account.')


class AccountsL(Resource):
    @auth.login_required
    def get(self):
        session = Session()
        raw_account = session.query(models.Account).all()

        response = resp(data=convert.jsonify(raw_account), status='success')

        session.close()
        return response, 200


    def post(self):
        parser = reqparse.RequestParser()

        # accepted ARGs from api
        parser.add_argument('username', type=str, help='help text')
        parser.add_argument('password', type=str, help='help text')
        args = parser.parse_args()

        #process user input
        if args['username'] != None and args['password'] != None:
            session = Session()
            existing_account = session.query(models.Account).filter_by(username=args['username']).first()
            if existing_account:
                response = resp(error='Account name already exists', status='failed')

                session.close()
                return response, 400

            new_account = models.Account(username=args['username'], password=args['password'])
            session.add(new_account)
            session.commit()

            response = resp(
                data=convert.jsonify((new_account,)),
                link='/accounts/{}'.format(new_account.id),
                status='success'
            )

            session.close()
            return response, 201

        else:
            response = resp(error='No post data', status='failed')
            return response, 400


class Items(Resource):
    @auth.login_required
    def get(self, id):

        session = Session()
        raw_item = functions.Item(session).get(id)
        if raw_item:
            response = resp(data=convert.jsonify((raw_item,)))

            session.close()
            return response

        else:
            response = resp(status='failed', error='item id doesnt exist')
            session.close()
            return response

    @auth.login_required
    def put(self, id):
        pass

    @auth.login_required
    def delete(self, id):
        session = Session()
        raw_account = session.query(models.Account).filter_by(username=auth.username()).first()
        raw_item = session.query(models.Item).filter_by(id=id).first()

        if auth.username() == raw_account.username:
            session.delete(raw_item)
            session.commit()

            response = resp(status='success', message='item successfully deleted')

            session.close()
            return response

        else:
            session.close()
            return resp(message='Items can only be deleted by the account of the uploader.')


class ItemsL(Resource):
    @auth.login_required
    def get(self):
        session = Session()
        raw_items = functions.Item(session).get()
        if raw_items:

            response = resp(data=convert.jsonify(raw_items))

            session.close()
            return response

        else:
            response = resp(status='failed', error='nothing in database')

            session.close()
            return response

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()

        # accepted ARGs from api
        parser.add_argument('name', type=str, help='help text')
        parser.add_argument('item_loc', type=str, help='help text')
        parser.add_argument('item_thumb', type=str, help='help text')
        parser.add_argument('attached', type=str, help='help text')
        parser.add_argument('item_type', type=str, help='help text')
        args = parser.parse_args()

        session = Session()
        args['author'] = auth.username()
        new_item = functions.Item(session).post(args)

        response = resp(message='New item created')

        session.close()
        return response


class Tags(Resource):
    @auth.login_required
    def get(self, id):
        pass

    @auth.login_required
    def put(self, id):
        pass

    @auth.login_required
    def delete(self, id):
        pass


class TagsL(Resource):
    @auth.login_required
    def get(self):
        pass

    @auth.login_required
    def post(self):
        pass









'''

class Galleries(Resource):
    def get(self, id):
        raw_gallery = Gallery.query.filter_by(id=id).first()

        if raw_gallery != None:

            response = resp(data=convert.jsonify((raw_gallery,)), status='success')
            return response, 200

        else:
            response = resp(status='failed', error='no such gallery id')
            return response, 400


    @auth.login_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('snaps', type=str, help='help text')
        parser.add_argument('private', type=str, help='help text')
        parser.add_argument('theme', type=str, help='help text')
        args = parser.parse_args()

        get_gallery = Gallery.query.filter_by(id=id).first()

        if get_gallery != None:
            if args['snaps']:
                raw_snap = Snap.query.filter_by(id=args['snaps']).first()
                if raw_snap != None:
                    get_gallery.snaps.append(raw_snap)
                    db.session.commit()
                    print('snaps is in there')

                else:
                    return resp(error='no such snap id')

            if args['private']:
                if get_gallery.private:
                    get_gallery.private = False
                    db.session.commit()
                else:
                    get_gallery.private = True
                    db.session.commit()

            if args['theme']:
                get_theme = Theme.query.filter_by(name=args['theme']).first()
                if get_theme:
                    get_gallery.theme.remove(get_gallery.theme[0])
                    get_gallery.theme.append(get_theme)
                    db.session.commit()

                    return resp(message='Theme has been changed.')


                else:
                    print('No such theme id')
            else:
                pass

        else:
            return resp(error='no such gallery id')


    @auth.login_required
    def delete(self, id):
        get_gallery = Gallery.query.filter_by(id=id).first()
        get_account = Account.query.filter_by(username=auth.username()).first()

        if get_gallery in get_account.galleries:
            db.session.delete(get_gallery)
            db.session.commit()

            response = resp(status='success', message='gallery successfully deleted')

            return response, 201

        else:
            return resp(message='gallery can only deleted by the account that posted it')


class GalleriesL(Resource):
    def get(self):
        accounts_galleries = Account.query.filter_by(username=auth.username()).first()
        if accounts_galleries:
            accounts_galleries = accounts_galleries.galleries

            response = resp(data=convert.jsonify(accounts_galleries), status='success')
            return response, 200

        else:
            response = resp(status='failed', error='Returned NoneType')
            return response, 401


    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, help='helper text')
        args = parser.parse_args()

        if args['title'] != None:
            raw_account = Account.query.filter_by(username=auth.username()).first()
            default_theme = Theme.query.filter_by(name='default').first()

            new_gallery = Gallery(title=args['title'])
            new_gallery.shareuuid = str(uuid.uuid4())
            new_gallery.theme.append(default_theme)
            new_gallery.account.append(raw_account)

            db.session.add(new_gallery)
            db.session.commit()

            response = resp(
                data=convert.jsonify((new_gallery,)),
                link='/galleries/{}'.format(new_gallery.id),
                status='success'
            )

            return response, 201

        else:
            response = resp(error='missing required data', message='')
            return response, 400

'''

# routes
api.add_resource(Entry, '/')
api.add_resource(Accounts, '/accounts/<id>')
api.add_resource(AccountsL, '/accounts')
api.add_resource(Items, '/items/<id>')
api.add_resource(ItemsL, '/items')
api.add_resource(Tags, '/tags/<id>')
api.add_resource(TagsL, '/tags')


if __name__ == '__main__':
    app.run(debug=True, port=5050)