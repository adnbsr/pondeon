#!flask/bin/python
import os
from flask import Flask,request,make_response,render_template
from urlparse import urlparse
from pymongo import Connection
from json import dumps
from time import ctime

from app import CustomEncoder

MONGO_URL = os.environ.get('MONGOHQ_URL')

if MONGO_URL:
  connection = Connection(MONGO_URL)
  db = connection[urlparse(MONGO_URL).path[1:]]
else:
  connection = Connection('localhost', 27017)
  db = connection['test']

app = Flask(__name__)


def jsonify(status=200, indent=4, sort_keys=True, **kwargs):
  response = make_response(dumps(dict(**kwargs), indent=indent, sort_keys=sort_keys,cls=CustomEncoder))
  response.headers['Content-Type'] = 'application/json; charset=utf-8'
  response.headers['mimetype'] = 'application/json'
  response.status_code = status
  return response

def getNextSequence(name):
    ret = db.users.find_and_modify(query = {'_id':'id'},update = {'$inc': {'seq': 1}},new = True)

    return int(ret['seq'])


@app.route('/')
def index():
    return make_response(render_template('index.html'))

@app.route('/api/v1.0/users')
def all_users():
    return jsonify(result = db.users.find())

@app.route('/api/v1.0/users/create',methods=['GET'])
def create_user():

    id =  getNextSequence('id')

    user = {
        'id': id,
        'createdAt': str(ctime()),
        'followers':[],
        'followings':[]
    }

    profile ={
        'id': id
    }

    for key, value in request.args.items(): profile[key] = value

    user['profile'] = profile

    db.users.insert(user)


    return jsonify(result = user)


@app.route('/api/v1.0/users/<id>/profile',methods=['GET'])
def get_profile(id):

    item = db.users.find_one({ 'id': int(id) })

    return jsonify(result = item['profile'])

@app.route('/api/v1.0/users/find',methods=['GET'])
def find_user():

    params = {}

    for key, value in request.args.items(): params[key] = value

    item = db.users.find(params)

    return jsonify(result = item)

@app.route('/api/v1.0/users/<id>/delete',methods=['GET'])
def delete_user(id):

    db.users.remove({"id":int(id)})

    return 'User is deleted!'

@app.route('/api/v1.0/users/<id>/update',methods=['GET'])
def update_user(id):

    for key, value in request.args.items():
        db.users.update({'id':int(id)},{'$set':{'profile.'+str(key):value}})

    item = db.users.find_one({'id':int(id)})

    return jsonify(result = item)

@app.route('/api/v1.0/users/<id>/follow',methods=['GET'])
def follow_user(id):

    req = {}
    for key, value in request.args.items(): req[key] = value

    follower = db.users.find_one({'id': int(id)})['profile']
    db.users.update({'id':int(req['id'])},{'$push':{'followers':follower}})

    following = db.users.find_one({'id': int(req['id']) })['profile']
    db.users.update({'id':int(id)},{'$push':{'followings':following}})

    return jsonify(result = following)


@app.route('/api/v1.0/users/<id>/followers',methods=['GET'])
def get_followers(id):

    item = db.users.find_one({ 'id': int(id) })['followers']

    return jsonify(followers= item)

@app.route('/api/v1.0/users/<id>/followings',methods=['GET'])
def get_followings(id):

    item = db.users.find_one({ 'id': int(id) })['followings']

    return jsonify(followings = item)

if __name__ == '__main__':
    app.run(debug=True)
