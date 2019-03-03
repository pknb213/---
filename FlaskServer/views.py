from builtins import enumerate
import flask_login
from FlaskServer import app
import os
import random
import datetime
import pymongo
import pandas
import copy
from flask import render_template, request, current_app, make_response, url_for, redirect, jsonify, abort
from bson.objectid import ObjectId  # For ObjectId to work
from flask_login import login_required, current_user, login_user, logout_user
from math import ceil
from collections import OrderedDict

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User:
    # ==========================================================================
    def __init__(self, user_id, email=None, passwd_hash=None,
                 authenticated=False):
        self.user_id = user_id
        self.email = email
        self.passwd_hash = passwd_hash
        self.authenticated = authenticated

    # ==========================================================================
    def __repr__(self):
        r = {
            'user_id': self.user_id,
            'email': self.email,
            'passwd_hash': self.passwd_hash,
            'authenticated': self.authenticated,
        }
        return str(r)

    # ==========================================================================
    def can_login(self, passwd_hash):
        return self.passwd_hash == passwd_hash

    # ==========================================================================
    def is_active(self):
        return True

    # ==========================================================================
    def get_id(self):
        return self.user_id

    # ==========================================================================
    def is_authenticated(self):
        return self.authenticated

    # ==========================================================================
    def is_anonymous(self):
        return False


USERS = {
    "user01": User("user01", passwd_hash='user'),
    "user02": User("user02", passwd_hash='user'),
    "user03": User("user03", passwd_hash='user'),
}


@login_manager.user_loader
def user_loader(user_id):
    return USERS[user_id]


@app.route("/api/auth_func", methods=['POST'])
@login_required
def auth_func():
    user = current_user
    json_res = {'ok': True, 'msg': 'auth_func(%s),user_id=%s'
                                   % (request.json, user.user_id)}
    return jsonify(json_res)


@app.route("/api/notauth_func", methods=['POST'])
def notauth_func():
    json_res = {'ok': True, 'msg': 'notauth_func(%s)'
                                   % request.json}
    return jsonify(json_res)


@app.route('/api/login', methods=['POST'])
def login():
    # user_id = request.json['user_id']
    # passwd_hash = request.json['passwd_hash']
    user_id = request.values.get('user_id')
    passwd_hash = request.values.get('passwd_hash')
    if user_id not in USERS:
        json_res = {'ok': False, 'error': 'Invalid user_id or password'}
    elif not USERS[user_id].can_login(passwd_hash):
        json_res = {'ok': False, 'error': 'Invalid user_id or password'}
    else:
        json_res = {'ok': True, 'msg': 'user <%s> logined' % user_id}
        USERS[user_id].authenticated = True
        login_user(USERS[user_id], remember=True)
    if not json_res['ok']:
        return jsonify(json_res)
    else:
        return render_template('/menu.html')


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    json_res = {'ok': True, 'msg': 'user <%s> logout' % user.user_id}
    logout_user()
    return jsonify(json_res)


class MongodbConnection:
    def __init__(self):
        # print(" ~~ ", sep = '\n')
        print("MongoDB init")
        self._ip = '222.106.48.150'
        self._port = 27019

    def db_client(self):
        return pymongo.MongoClient(self._ip, self._port)

    def db_conn(self, client, coll):
        try:
            db = client['ERP_test']
        except Exception as e:
            print("Connected fail (Database)")
            print(e)
            client.db_close()
        print("Connect", end=' >> ')
        return db[coll]
        # return db.get_collection(coll)

    def db_close(self):
        print("Disconnect")
        return self.db_client().close()


class Rows:
    def __init__(self):
        print("Rows Class init")
        self._DB_object = MongodbConnection()

    # def production_main_list(self):

    def main_table_rows(self):
        print('Load - Class main_table_rows()')
        result_rows = []
        # show key is the most recently value.
        query = {"show": {'$eq': '1'}}
        try:
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'history')
            _history_list = list(rows_collection.find(query))  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.model()", end=" >> ")
            print(e)

        _product_id_list = []
        _location_list = []
        _state_list = []
        _date_list = []
        _reason_list = []
        for row in _history_list:
            _product_id_list.append(row['product_id'])
            _location_list.append(row['location'])
            _state_list.append(row['state'])
            _date_list.append(row['date'])
            _reason_list.append(row['reason'])

        _week_list = []
        _sn_list = []
        _model_list = []
        _model_id_list = []
        try:
            product_info_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'product_info')
        except Exception as e:
            print("DB_error : Class Rows.model()", end=" >> ")
            print(e)
        for product_id in _product_id_list:
            query = {"_id": {'$eq': ObjectId(product_id)}}
            try:
                product_info_cursor = product_info_collection.find(query)  # cursor type
            except Exception as e:
                print("DB_error : Class Rows.model()", end=" >> ")
                print(e)
            for product_info_dic in product_info_cursor:
                # print("info_dic : ", end="")
                # print(product_info_dic)
                _week_list.append(product_info_dic['week'])
                _sn_list.append(product_info_dic['sn'])
                _model_id_list.append(product_info_dic['model_id'])
                _model_list.append(product_info_dic['model'])

        for i in range(0, len(_product_id_list)):
            res = {"product_info_id": _product_id_list[i], "model": _model_list[i], "sn": _sn_list[i],
                   "week": _week_list[i], "location": _location_list[i], "state": _state_list[i],
                   "reason": _reason_list[i], 'model_id': _model_id_list[i]}
            result_rows.append(res)
        self._DB_object.db_close()
        print("Main Table : ", end="")
        print(result_rows)

        if not result_rows:
            print('empty')
        elif result_rows:
            print('exist')
        return result_rows

    def production_main_model(self):
        print('Load - Class production_main_model()')
        try:
            # db_object = Mongodb_connection()
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'model')
            rows_list = list(rows_collection.find())  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.model()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        # print("all list")\
        return rows_list

    def production_main_history(self):
        print('Load - Class production_main_history()')
        try:
            # db_object = Mongodb_connection()
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'history')
            rows_list = list(rows_collection.find())  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.history()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        # print("all list")\
        return rows_list

    def production_main_info_list(self):
        print('Load - Class production_main_info_list()')
        try:
            # db_object = Mongodb_connection()
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'product_info')
            rows_list = list(rows_collection.find())  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.info()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        # print("all info list")\
        return rows_list

    def production_main_specific_date_list(self):
        print('Load - Class production_main_specific_date_list()')
        page = 'p_page'
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        now = date.split('-')
        for i in range(0, 3):
            now[i] = int(now[i])
        now = week_num(now[0], now[1], now[2])  # year, month, day

        try:
            rows_list = search_query(now, now, page)
        except Exception as e:
            print("DB_error : production_main()", end=" >> ")
            print(e)
            return render_template('404.html'), 404

        # print("date list")
        return rows_list

    def week(self):
        print('Load - Class week()')
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        now = date.split('-')
        for i in range(0, 3):
            now[i] = int(now[i])
        week = week_num(now[0], now[1], now[2])
        return week

    def manufacture_list(self):
        print('Load - Class manufacture_list()')
        try:
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'manufacture')
            rows_list = list(rows_collection.find())  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.manufacture()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        # print("all info list")
        # rows_list = [{"model": "씨발", "new_product": "444"}]
        return rows_list

    def sales_list(self):
        print('Load - Class sales_list()')
        try:
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'project_num')
            rows_list = list(rows_collection.find())  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.manufacture()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        if not rows_list:
            print('Database is Empty')
            rows_list = None
        print("Sales Row List : ", end='')
        print(rows_list)
        return rows_list

    def date(self):
        print('Load - Class date()')
        return datetime.datetime.today().strftime('%Y-%m-%d')


def make_read_excel():
    import numpy as np
    # make excel file
    '''
    writer = pandas.ExcelWriter('./FaskServer/static/excel/test.xlsx')
    df = pandas.DataFrame({"col_{}".format(i):list(np.random.randint(0, 100, 100)) for i in range(0, 8)})
    df.to_excel(writer, 'sheet1')
    writer.save()
    
    ## read excel file
    df = pandas.read_excel('./FaskServer/abc.xlsx', sheet_name='Sheet1')
    ## 아주 다행히도, dataframe을 html 문서로 바로 변환해주는 형식이 있습니다.
    #return df.to_html()
    print(df.head())
    if os.path.isfile(df):
        xl = pandas.ExcelFile('static/excel/생산계획.xlsx')
    else:
        print("Eroor < load fail : %s" % (df))
    return xl.parse(''.join(xl.sheet_names))
    '''


@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    user = USERS["user01"]
    login_user(user)
    object = Rows()
    return render_template('test.html', object=object)


@app.route('/login')
def test_login():
    return render_template('login.html')


@app.route('/test_login')
def loginTest():
    user = user_loader('user01')
    login_user(user)
    return "User : %s" % user


@app.route('/post_login', methods=["POST"])
def postLogin():
    user_id = request.values.get("user_id")
    user_pw = request.values.get("passwd_hash")
    print(user_id)
    print(user_pw)

    user = User(user_id, passwd_hash=user_pw)
    print(user)
    print(user.can_login(user.passwd_hash))

    user2 = USERS["user01"]
    print(user2)
    print(user2.can_login(user2.passwd_hash))

    if user in USERS:
        user = USERS[user_id]
        print(user.can_login(user_pw))

    if user.is_authenticated():
        print("인즘됨")
        login_user(user, remember=True)

    else:
        print("인증안됨")

    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    return redirect('/main')


@app.route('/logout')
@login_required
def logoutTest():
    logout_user()
    return "You are now logged out"


@app.route('/main')
@login_required
def main_menu():
    return render_template('menu.html')


@app.route('/upload')
def ckeditor4():
    return render_template('ckeditor4.html')


@app.route('/')
def production_main():
    row_object = Rows()
    return render_template('production_main.html', specific_list=None, object=row_object)


@app.route('/filtering', methods=["POST"])
def filtering():
    _filter = request.values.get('filter')
    _sub_filter = request.values.get('sub_filter')
    _sDate = request.values.get('sDate')
    _eDate = request.values.get('eDate')

    print("Get value : ")
    print(_filter + ' ' + _sub_filter + ' ' + _sDate + ' ' + _eDate)

    _sDate = _sDate.split('-')
    _eDate = _eDate.split('-')
    for i in range(0, 3):
        _sDate[i] = int(_sDate[i])
        _eDate[i] = int(_eDate[i])
    s_week = week_num(_sDate[0], _sDate[1], _sDate[2])
    e_week = week_num(_eDate[0], _eDate[1], _eDate[2])

    query = {
        "$and": [
            {
                u"week": {
                    u"$gte": s_week
                }
            },
            {
                u"week": {
                    u"$lte": e_week
                }
            },
            {
                u"show": {
                    u"$eq": '1'
                }
            }
        ]
    }

    try:
        _DB_object = MongodbConnection()
        rows_collection = _DB_object.db_conn(_DB_object.db_client(), 'product_info')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : Class Rows.manufacture()", end=" >> ")
        print(e)
    finally:
        _DB_object.db_close()

    model_rows = []
    model_coll = _DB_object.db_conn(_DB_object.db_client(), 'model')
    for row in rows_list:
        query = {"_id": {'$eq': ObjectId(row['model_id'])}}
        model_rows.extend(list(model_coll.find(query)))  # cursor type -> list type

    history_rows = []
    history_coll = _DB_object.db_conn(_DB_object.db_client(), 'history')
    for row in rows_list:
        query = {"$and": [{"product_id": {'$eq': str(row['_id'])}}, {'show': {'$eq': '1'}}]}
        history_rows.extend(list(history_coll.find(query)))  # cursor type -> list type

    print("Date match rows :")
    for row in rows_list:
        print(row)
    print("Reference model rows :")
    for row in model_rows:
        print(row)

    print("Reference history rows :")
    for row in history_rows:
        print(row)

    merge_list = []
    for i in range(0, len(rows_list)):
        new_dic = {}
        new_dic.update(rows_list[i])
        new_dic.update(model_rows[i])
        new_dic.update(history_rows[i])
        merge_list.append(new_dic)

    print("Merge List")
    for lis in merge_list:
        print(lis)

    if _filter == '전체':
        m_value = None
        l_value = None
        s_value = None
    elif _filter == '모델':
        m_value = _sub_filter
        l_value = None
        s_value = None
    elif _filter == '위치':
        m_value = None
        l_value = _sub_filter
        s_value = None
    elif _filter == '상태':
        m_value = None
        l_value = None
        s_value = _sub_filter
    else:
        m_value = _sub_filter
        l_value = _sub_filter
        s_value = _sub_filter

    _filter_dic = {'model': m_value, 'location': l_value, 'state': s_value}

    print(_filter_dic)

    first_filtering_list = []
    second_filtering_list = []
    third_filtering_list = []
    print("> Model Filtering")
    if _filter_dic['model'] is not None:
        for idx, merge_row in enumerate(merge_list):
            if merge_row.get('model') == _filter_dic['model']:
                print(idx, merge_row)
                first_filtering_list.append(merge_row)
            else:
                print("Delete : ", end='')
                print(idx, merge_row)
    else:
        first_filtering_list = merge_list

    print(">> Location Filtering")
    if _filter_dic['location'] is not None:
        for idx, merge_row in enumerate(first_filtering_list):
            if merge_row.get('location') == _filter_dic['location']:
                print(idx, merge_row)
                second_filtering_list.append(merge_row)
            else:
                print("Delete : ", end='')
                print(idx, merge_row)
    else:
        second_filtering_list = first_filtering_list

    print(">>> State Filtering")
    if _filter_dic['state'] is not None:
        for idx, merge_row in enumerate(second_filtering_list):
            if merge_row.get('state') == _filter_dic['state']:
                print(idx, merge_row)
                third_filtering_list.append(merge_row)
            else:
                print("Delete : ", end='')
                print(idx, merge_row)
    else:
        third_filtering_list = second_filtering_list

    print("After Filtering")
    if not third_filtering_list:
        print("After filtering . . . List is Empty")
    else:
        for lis in third_filtering_list:
            print(lis)
    row_object = Rows()

    return render_template('production_main.html', specific_list=third_filtering_list, object=row_object)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def search_query(sdate, edate, page):
    # rows_list = list(rows_collection.find({'$and': [{'week': {'$gte': sdate}},{'week': {'$lte': edate}}]}))
    # query = {}
    # query["$and"] = [
    if page == 'p_page':
        collection_of_model = 'model'
        collection_of_history = 'history'
        collection_of_product_info = 'product_info'
        product_info_query = {"$and": [
            {
                u"week": {
                    u"$gte": sdate
                }
            },
            {
                u"week": {
                    u"$lte": edate
                }
            },
            {
                u"show": {
                    u"$eq": '1'
                }
            }
        ]}
    # Not use
    elif page == 's_page':
        coll = 'test2'
        query = {"$and": [
            {
                u"_product_week": {
                    u"$gte": sdate
                }
            },
            {
                u"_product_week": {
                    u"$lte": edate
                }
            },
            {
                u"_show": {
                    u"$eq": '1'
                }
            }
        ]}

    else:
        print("page parameter is wrong")

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), collection_of_product_info)
        rows_list = list(rows_collection.find(product_info_query))  # cursor type -> list type
        list_of_model_id = []
        list_of_history_id = []
        for row in rows_list:
            list_of_model_id.append(row['model_id'])
            list_of_history_id.append(str(row['_id']))
        # print("list_of_model_id : ", end="")
        # print(list_of_model_id)
        # print("list_of_history_id : ", end="")
        # print(list_of_history_id)

        rows_collection = db_object.db_conn(db_object.db_client(), collection_of_model)
        list_of_model = []
        for model_id in list_of_model_id:
            model_query = {u"_id": {u"$eq": ObjectId(model_id)}}
            list_of_model.extend(list(rows_collection.find(model_query)))  # cursor type -> list type

        rows_collection = db_object.db_conn(db_object.db_client(), collection_of_history)
        list_of_history = []
        for history_id in list_of_history_id:
            history_query = {"$and": [{u"product_id": {u"$eq": history_id}}, {u"show": {u"$eq": '1'}}]}
            list_of_history.extend(list(rows_collection.find(history_query)))  # cursor type -> list type

    except Exception as e:
        print("DB_error : search_query()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    new_list = []
    for i in range(0, len(rows_list)):
        new_dic = {'model': list_of_model[i]['model'],
                   'sn': rows_list[i]['sn'],
                   'week': rows_list[i]['week'],
                   'state': list_of_history[i]['state'],
                   'location': list_of_history[i]['location'],
                   '_id': rows_list[i]['_id']}
        new_list.append(new_dic)
    print("Result List : ")
    for row in new_list:
        print(row)

    return new_list


def week_num(year, mon, day):
    n = datetime.datetime(year, mon, day)
    # print(n) # calender date
    n = n.isocalendar()
    # print(n) # week num
    n = list(n)  # casting tuple -> list
    wn = str(n[1])
    if len(wn) == 1:
        wn = '0' + wn
    year = str(year)  # casting int -> str
    result = year[2:4] + str(wn)  # slice 2~4 char + week num
    return result


def insert_model(collection, model):
    # Add Meta Data Later.
    query = {'model': model}
    return collection.insert(query)  # Return value is ObjectId


def insert_history(collection, args_list):
    query = {'product_id': args_list[0],
             'show': '1',
             'date': args_list[1],
             'location': args_list[2],
             'state': args_list[3],
             'reason': args_list[4]}
    return collection.insert(query)


def insert_product_info(collection, args_list):
    query = {'model_id': args_list[0], 'model': args_list[1], 'sn': args_list[2], 'header': args_list[3],
             'week': args_list[4], 'quality': args_list[5], 'show': args_list[6]}

    return collection.insert(query)  # Return value is ObjectId


@app.route('/insert_data', methods=["POST"])
def insert_data():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    now = date.split('-')
    for i in range(0, 3):
        now[i] = int(now[i])
    now = week_num(now[0], now[1], now[2])

    # Input name value
    _model = request.values.getlist("model")
    _sn = request.values.getlist("sn")
    _header = request.values.getlist("header")

    for i in range(0, len(_model)):
        try:
            db_object = MongodbConnection()
            rows_collection = db_object.db_conn(db_object.db_client(), 'model')
            _model_id = str(insert_model(rows_collection, _model[i]))
        except Exception as e:
            db_object.db_close()
            print("DB_error : insert_model()", end=" : ")
            print(e)

        # Auto value
        _week = now
        _quality = 'N'
        _show = '1'
        auto_values = [_model_id, _model[i], _sn[i], _header[i], _week, _quality, _show]

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
            _product_id = str(insert_product_info(rows_collection, auto_values))
        except Exception as e:
            print("DB_error : insert_product_info()", end=" >> ")
            print(e)
        finally:
            db_object.db_close()

        # History value
        _date = date
        _location = '대전'
        _state = '재고'  # 재고, 출고, 폐기
        _reason = '신규생산'  # 신규생산, 판매, 기증, 내수용, A/S, 불량, 반납, 이동
        history_values = [_product_id, _date, _location, _state, _reason]

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'history')
            insert_history(rows_collection, history_values)
        except Exception as e:
            db_object.db_close()
            print("DB_error : insert_history()", end=" : ")
            print(e)

    return redirect('/')


def find_production_info_item(coll, product_id):
    query = {
        u"_id": ObjectId(product_id)
    }
    return coll.find(query)


def find_history_all_item(coll, product_id):
    query = {
        u"product_id": {
            u"$eq": product_id
        }
    }
    return coll.find(query)


@app.route('/getDetailTable')
def getDetailTable():
    _id = request.args.get('product_info_id')
    print("Detail Agix : ", end='')
    print(_id)

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'history')
        history_list = list(find_history_all_item(rows_collection, _id))
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
        product_info_list = list(find_production_info_item(rows_collection, _id))
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    print("Product info : ", end='')
    print(product_info_list)
    product_info_list[0].pop('_id')

    for result in history_list:
        result.pop('_id')
        product_info_list.append(result)

    print(product_info_list)
    return jsonify(product_info_list)


def find_history_item(coll, product_id):
    query = {
        "$and":
            [
                {
                    u"product_id": {
                        u"$eq": product_id
                    }
                },
                {
                    'show': {'$eq': '1'}
                }
            ]
    }
    return coll.find(query)


@app.route('/getStateChangeTable')
def getStateChangeTable():
    _product_info_id = eval(request.args.get('product_info_id'))
    print("Checkbox Agix : ", end='')
    print(_product_info_id)
    if not len(_product_info_id):
        print("Not have a Checked box")
        return jsonify(_product_info_id)

    result_list = []
    for _id in _product_info_id:
        try:
            db_object = MongodbConnection()
            rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
            product_list = list(find_production_info_item(rows_collection, _id))
        except Exception as e:
            print("DB_error : getStateChangeTable() - product_info", end=" : ")
            print(e)

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'history')
            history_list = list(find_history_item(rows_collection, _id))
        except Exception as e:
            print("DB_error : getStateChangeTable() - history", end=" : ")
            print(e)
        finally:
            db_object.db_close()

        product_list[0].pop('_id')
        history_list[0].pop('_id')

        result_dic = {}
        result_dic.update(product_list[0])
        result_dic.update(history_list[0])
        result_list.append(result_dic)

    print(result_list)

    return jsonify(result_list)


@app.route('/state_change', methods=["POST"])
def state_change():
    def getStateFromReason(reason):
        state_map = {
            '신규생산': '재고',
            '반납': '재고',
            '이동': '재고',
            '판매': '출고',
            '기증': '출고',
            '내수용': '출고',
            'A/S': '출고',
            '불량': '폐기'
        }
        return state_map[reason]

    # if not len(request.values.getlist("check_box")):
    #     print("state_change rows is empty")
    #     return redirect('/')
    # else:
    try:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        _date = {'date': date}
        # _checked_id = request.values.getlist("check_box")  # Checked the Object _id value
        _id = request.values.getlist("id")
        _location = request.values.getlist("location")
        _reason = request.values.getlist("reason")
        row_list = []
        print("GET State Change List")
        print(_id)
        print(_location)
        print(_reason)
        for i in range(0, len(_id)):
            _state = getStateFromReason(_reason[i])
            row_list.append({'id': _id[i], 'location': _location[i],
                             'state': _state, 'reason': _reason[i]})
    except Exception as e:
        print("POST_error : state_change()", end=" >> ")
        print(e)
    else:
        # print(_checked_id, end=" ")
        print("POST row_list : ")
        for row in row_list:
            print(row)
    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'history')
        # for i in range(0, len(_checked_id)):
        for j in range(0, len(row_list)):
            # if _checked_id[i] == row_list[j]['id']:
            print("Change !! ", end=" ")
            # print(_checked_id[i], end=" <-- ")
            print(row_list[j])
            # return find() -> Cursor Type
            # return insert() -> Object Type
            # return update() -> Dict Type

            p_id = row_list[j]['id']
            update_history(rows_collection, p_id)
            data = [row_list[j]['id'], date, row_list[j]['location'],
                    row_list[j]['state'], row_list[j]['reason']]
            insert_history(rows_collection, data)

    except Exception as e:
        print("DB_error : state_change()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/')


def update_history(collection, product_id):
    match_query = {'product_id': product_id}
    value_query = {'$set': {'show': '0'}}
    return collection.update(match_query, value_query, multi=True)


@app.route('/manufacture_main')
def manufacture_main():
    object_rows = Rows()
    return render_template('manufacture.html', specific_list=None, object=object_rows)


def insert_manufacture_info(collection, data_list):
    # Add Meta Data Later.
    query = {'week': data_list[0], 'model': data_list[1], 'number': data_list[2], 'date': data_list[3]}
    return collection.insert(query)  # Return value is ObjectId


def find_number_of_model(coll, arg, arg2):
    query = {
        u"model": {
            u"$eq": arg
        },
        u"week": {
            u"$eq": arg2
        }
    }
    return coll.find(query).count()


def search_week(coll, data_list):
    query = {}
    return coll.find(query)


# 생산 page
@app.route('/manufacture_insert', methods=["POST"])
def manufacture_insert():
    date = datetime.datetime.today().strftime('%Y-%m-%d')

    # Input name value
    _week = request.values.get("week")
    _model = request.values.getlist("model")
    _number = request.values.getlist("number")

    print("Insert Get Data : ", end='')
    print(_week, end=' ')
    print(_model, end=' ')
    print(_number, end=' ')
    print(type(_number), end=' ')
    print(len(_model))
    _data_list = []
    for i in range(0, len(_model)):
        _list = [_week, _model[i], _number[i], date]
        _data_list.append(_list)
    print("Data List : ")
    for data in _data_list:
        print(data)
    try:
        db_object = MongodbConnection()
        for i in range(0, len(_data_list)):
            rows_collection = db_object.db_conn(db_object.db_client(), 'manufacture')
            _insert_id = insert_manufacture_info(rows_collection, _data_list[i])
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/manufacture_main')


@app.route("/getProductData")
def getProductData():
    # 모델명을 받아서 model 콜렉션에서 해당 일치하는 모델의 수를 넘겨준다.
    # 그 수량이 완료 필드에 들어가야한다. Aging은 넘겨줘서 계산하도록 한다.
    # 완료 수량 = 재고 DB에 있는 모델의 수

    _model_list = eval(request.args.get('model_list'))
    _week_list = eval(request.args.get('week_list'))
    _table_list = eval(request.args.get('table_list'))
    print(_model_list)

    # print("Model list : ")
    # for _model in _model_list:
    #     print(_model)
    # print("Week list : ")
    # for _week in _week_list:
    #     print(_week)
    # print("Table row : ")
    # for table_row in _table_list:
    #     print(table_row)

    count_dic = {}
    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
        for i in range(0, len(_model_list)):
            count_dic[_model_list[i]] = find_number_of_model(rows_collection, _model_list[i], _week_list[i])
        # for model in _model_list:
        #    count_dic[model] = find_number_of_model(rows_collection, model)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    print("Number of Model Dic : ")
    print(count_dic)

    print("Result rows : ")
    for row in _table_list:
        result = list(row.values() & count_dic.keys())
        row[result[0]] = count_dic[result[0]]
        print(row)

    return jsonify(_table_list)


# 영업 page
@app.route('/sales_main')
def sales_main():
    row_object = Rows()

    return render_template('sales_main.html', specific_rows=None, object=row_object)


def insert_project_num(collection, data_list):
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    query = {'pn': data_list[0], 'project_name': data_list[1], 'date': date}
    return collection.insert(query)


@app.route('/registerPN', methods=['POST'])
def project_number_register():
    _number_of_pn = request.values.get('pn_field')
    _project_name = request.values.get('project_name_field')
    print("GET PN : ", end='')
    print(_number_of_pn, end='   ')
    print(" Name : ", end='')
    print(_project_name)
    insert_data_list = [_number_of_pn, _project_name]

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'project_num')
        _insert_id = insert_project_num(rows_collection, insert_data_list)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/sales_main')


def insert_partner_list(collection, data_list):
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    query = {'classification': data_list[0], 'partner_name_field': data_list[1], 'b_field': data_list[2],
             'address_field': data_list[3],
             'header_field': data_list[4], 'phone_field': data_list[5], 'email_field': data_list[6],
             'var_field': data_list[7],
             'date': date}
    return collection.insert(query)


@app.route('/registerPartner', methods=['POST'])
def partner_register():
    _classification = request.values.get('classification')
    _partner_name = request.values.get('partner_name_field')
    _b = request.values.get('b_field')
    _address = request.values.get('address_field')
    _header = request.values.get('header_field')
    _phone = request.values.get('phone_field')
    _email = request.values.get('email_field')
    _var = request.values.get('var_field')
    print("GET  Classification: ", end='')
    print(_classification, end='   ')
    print(" Partner_name_field : ", end='')
    print(_partner_name)
    print("b_field : ", end='')
    print(_b, end='   ')
    print(" Address_field : ", end='')
    print(_address)
    print("Header_field : ", end='')
    print(_header, end='   ')
    print("Phone_field : ", end='')
    print(_phone)
    print("Email_field PN : ", end='')
    print(_email, end='   ')
    print("Var_field : ", end='')
    print(_var)
    insert_data_list = [_classification, _partner_name, _b, _address,
                        _header, _phone, _email, _var]

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'project_num')
        _insert_id = insert_partner_list(rows_collection, insert_data_list)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()
    return redirect('/sales_main')


# 통계 page
@app.route('/statistics_main')
def statistics_main():
    row_object = Rows()
    return render_template('statistics_main.html', specific_rows=None, object=row_object)


@app.route('/getBarGraph')
def getBarGraph():
    def distinct_week_value_list(coll):
        return coll.distinct('week')

    def distinct_model_value_list(coll):
        return coll.distinct('model')

    def find_number_of_model_from_week_and_model(coll, _week, _model):
        query = {
            "$and":
                [
                    {
                        u"week": {
                            u"$eq": _week
                        }
                    },
                    {
                        u'model': {'$eq': _model}
                    }
                ]
        }
        return coll.find(query).count()

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
        week_list = distinct_week_value_list(rows_collection)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)

    print(week_list)

    try:
        model_list = distinct_model_value_list(rows_collection)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)

    print(model_list)

    number_of_model_list = []
    number_of_model_dic = {}
    temp_dic = {}
    try:
        for _week in week_list:
            for _model in model_list:
                number_of_model_dic[_model] = find_number_of_model_from_week_and_model(rows_collection, _week, _model)
                temp_dic = number_of_model_dic.copy()
            number_of_model_list.append(temp_dic)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    # for val in number_of_model_list:
    #     print(val)

    result = [week_list, model_list, number_of_model_list]

    for val in result:
        for item in val:
            print(item)

    return jsonify(result)


@app.route('/getBarGraph2')
def getBarGraph2():
    def distinct_week_value_list(coll):
        return coll.distinct('week')

    def distinct_model_value_list(coll):
        return coll.distinct('model')

    def find_number_of_model_from_week_and_model(coll, _week, _model):
        query = {
            "$and":
                [
                    {
                        u"week": {
                            u"$eq": _week
                        }
                    },
                    {
                        u'model': {'$eq': _model}
                    }
                ]
        }
        cs = coll.find(query)
        _list = []
        for cs_item in cs:
            _list.extend(copy.deepcopy(cs_item['number']))
        # print(_list)
        return sum(map(int, _list))

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'manufacture')
        week_list = distinct_week_value_list(rows_collection)
    except Exception as e:
        print("DB_error : distinct_manufacture", end=" : ")
        print(e)

    print(week_list)

    try:
        model_list = distinct_model_value_list(rows_collection)
    except Exception as e:
        print("DB_error : distinct_manufacture", end=" : ")
        print(e)

    print(model_list)

    number_of_model_list = []
    number_of_model_dic = {}
    temp_dic = {}
    try:
        for _week in week_list:
            for _model in model_list:
                number_of_model_dic[_model] = find_number_of_model_from_week_and_model(rows_collection, _week, _model)
                temp_dic = number_of_model_dic.copy()
            number_of_model_list.append(temp_dic)
    except Exception as e:
        print("DB_error : find_number_of_model_from_week_and_model()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    # for val in number_of_model_list:
    #     print(val)

    result = [week_list, model_list, number_of_model_list]

    for val in result:
        for item in val:
            print(item)

    return jsonify(result)


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/excel_table', methods=['POST'])
def excel_table():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                print('No file part')
                return redirect('/insert_plan')
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                print('No selected file')
                return redirect('/insert_plan')
            if file and allowed_file(file.filename):
                # filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

                df = pandas.read_excel('./FlaskServer/static/excel/생산계획.xlsx', sheet_name='sheet1', engine='xlrd')

                print(df)
                print(type(df))
                # print(df['월'])

                rows_list = [list(df.loc[0]), list(df.loc[1]), list(df.loc[2]), list(df.loc[3]), list(df.loc[4])]
                # rows_list.append(list(df.loc[4]))

                return render_template('plan_list.html', rows=rows_list)
                # return redirect(url_for('insert_plan', filename=file.filename))
    except Exception as e:
        print(" Excel_error : excel_table()", end=" >> ")
        print(e)
        render_template('404.html'), 404


@app.route('/ckprocess', methods=['POST'])
def ckeditor4_process():
    return redirect('/')


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@app.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor4 file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'img', rnd_name)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('img', rnd_name))
    else:
        error = 'post error'
    res = """<script type="text/javascript"> 
             window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
             </script>""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response
