from flask import Flask, render_template, session, request, jsonify, url_for, redirect, Response, flash
from bson import ObjectId
from Flask.db.pymongodb import model_coll, history_coll, manufacture_coll, product_info_coll, users_coll, mongoClient
import json, os, datetime
from pytz import timezone, utc
from ast import literal_eval
from flask_login import *
import functools
KST = timezone('Asia/Seoul')
fmt = '%Y-%m-%d %H:%M:%S %Z%z'


app = Flask(__name__, template_folder= os.getcwd() + '/Flask/templates', static_folder=os.getcwd() + '/Flask/static')

app.config.update(

    #Set the secret key to a sufficiently ranrefactoring 단계dom value
    SECRET_KEY=os.urandom(24),

    #Set the session cookie to be secure
    SESSION_COOKIE_SECURE=True,

    #Set the session cookie for our app to a unique name
    SESSION_COOKIE_NAME='YourAppName-WebSession',

    #Set CSRF tokens to be valid for the duration of the session. This assumes you’re using WTF-CSRF protection
    WTF_CSRF_TIME_LIMIT=None

)


class User(UserMixin):
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = id
        self.password = ["passwd"] if users_coll.find_one({'user_id': user_id}) else user_id


class LoginRequired:
    def __init__(self, param = ''):
        self.allowed = []
        self.unallowed = []
        if param == '': return
        for arg in param.split(','):
            if arg[0] == '-':
                self.unallowed.append(arg[1:])
            else:
                self.allowed.append(arg)

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, ** kwargs):
            if not current_user.is_authenticated:
                return "NOT LOGGED"
            if current_user.name in self.unallowed:
                return "FORBIDDEN"
            if len(self.allowed)==0 or current_user.name in self.allowed:
                return fn(*args, **kwargs)
            else:
                return "NOT ALLOWED"
        return decorated


def check_user(id, passwd):
    try:
        print(users_coll.find_one({'id': id}))
        return users_coll.find_one({'id': id})["passwd"] == passwd
    except:
        return False


def form2dict(form):
    d = dict(form)
    for k, v in d.items():
        if type(v) is list and len(v) == 1 :
            d[k] = v[0]
    return d


def dict2jsgrid(item):
    if item is None:
        return item
    res = dict(item)
    for k, v in res.items():
        if type(v) is ObjectId:
            res[k] = str(v)
        if type(v) is dict:
            res[k] = cursor2jsgrid(res[k])
            res[k] = dict(res[k][0])
    return res


def cursor2jsgrid(cur):
    if type(cur) is not dict:
        res = list(cur)
    elif type(cur) is dict:
        res = [cur]
    for i in range(len(res)):
        res[i] = dict2jsgrid(res[i])
    return res


def getKeys(collection):
    """ Example : print(getKeys('history')) """
    pipeline = [
        {"$project": {"arrayofkeyvalue": {"$objectToArray": "$$ROOT"}}}, {"$unwind": "$arrayofkeyvalue"},
        {"$group": {"_id": None, "allkeys": {"$addToSet": "$arrayofkeyvalue.k"}}}
    ]

    _collection = mongoClient["ERP_refacDB"][collection]
    result_list = list(_collection.aggregate(pipeline))
    return result_list[0]['allkeys']


def getKeysFromAllDocument(collection):
    """  Example : print(getKeysFromAllDocument("history"))  """
    pipeline = [
        {"$project": {"arrayofkeyvalue": {"$objectToArray": "$$ROOT"}}}, {"$project": {"keys": "$arrayofkeyvalue.k"}}
    ]

    _collection = mongoClient["ERP_refacDB"][collection]
    result_list = list(_collection.aggregate(pipeline))

    return result_list


def date2week(date):
    ' ex) 2019-04-16 '
    date = date.split('-')
    if len(date) != 3:
        return False
    for i in range(len(date)):
        date[i] = int(date[i])
    year = date[0]
    month = date[1]
    day = date[2]

    n = datetime.datetime(year, month, day)
    n = list(n.isocalendar())

    wn = str(n[1])
    if len(wn) == 1:
        wn = '0' + wn

    year = str(year)
    result = year[2:4] + str(wn)
    return result


def test():
    a = list(range(0,100))
    print(a)
    print("-----------------------------------------------------")

    i = len(a) - 1
    while i >= 0:
        if a[i] % 2 == 0:
            del a[i]
        i = i - 1

    print(a)

def resultCheck(arg):
    print(" Argument Check Function : ", end="")
    print(arg)
    print("Arg is '' ?  : ", end="")
    if arg is '':
        print('True')
    print("Arg is False ?  : ", end="")
    if arg is False:
        print('True')
    print("Arg is not ?  : ", end="")
    if not arg:  # same the if arg == False
        print('True')
    print("Arg is none ?  : ", end="")
    if arg is None:
        print('True')
    print("Arg == '' ?  : ", end="")
    if arg == '':
        print('True')
    print("Arg is [''] ?  : ", end="")
    if arg is ['']:
        print('True')
    print("Arg is [] ?  : ", end="")
    if arg is []:
        print("True")


def string2dicCheck(_str):
    print('\nString : ')
    print(_str)
    print(type(_str))
    print('\nUsing the json.loads() : ')
    json_dic = json.loads(_str)
    print(json_dic)
    print(type(json_dic))
    print('\nUsing the json.dumps() : ')
    json_dumps = json.dumps(json_dic)
    print(json_dumps)
    print(type(json_dumps))
    print('\nUsing the literal_eval() : ')
    eval_dic = literal_eval("\'" + _str + "\'")
    print(eval_dic)
    print(type(eval_dic))


def pipeline(location, model):
    _pipeline = [
        {
            "$lookup":
                {
                    "from": "history",
                    "localField": "_id",
                    "foreignField": "product_id",
                    "as": "history_coll"
                }

        },
        {
            "$unwind": "$history_coll"
        },
        {
            "$lookup":
                {
                    "from": "model",
                    "localField": "model_id",
                    "foreignField": "_id",
                    "as": "model_coll"
                }
        },
        {
            "$unwind": "$model_coll"
        },
        {
            "$match":
                {
                    "$and":
                        [
                            {'history_coll.show': '1'},
                            {'history_coll.location': location},
                            {'model_coll.model': model}
                        ]

                }
        },
        {
            "$project":
                {
                    "history_coll.location": 1, "model_coll.model": 1
                }
        }
    ]
    return _pipeline

