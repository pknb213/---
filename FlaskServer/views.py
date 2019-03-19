import flask_login
from FlaskServer import app
import os
import random
import datetime
from datetime import timedelta
import pandas
import copy
from flask import render_template, request, current_app, make_response, url_for, redirect, jsonify, abort, session
from bson.objectid import ObjectId  # For ObjectId to work
from flask_login import login_required, current_user, login_user, logout_user
import FlaskServer.ajax as ajax
import FlaskServer.query as query
from FlaskServer.rowObejct import Rows
from FlaskServer.pymongo import MongodbConnection

login_manager = flask_login.LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = u"Session timed out, please re-login"
login_manager.needs_refresh_message_category = "info"


@app.before_first_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


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
        #return jsonify(json_res)
        return render_template('error.html', title='Login Fail :(', str='Please... retry the login.', url='main_login')
    else:
        return render_template('menu.html')


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    json_res = {'ok': True, 'msg': 'user <%s> logout' % user.user_id}
    logout_user()
    return jsonify(json_res)


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


@app.route('/')
def main_login():
    return render_template('login.html')


@app.route('/menu')
@login_required
def testing():
    return render_template('menu.html')


@app.route('/test_login')
def loginTest():
    user = user_loader('user01')
    login_user(user)
    return "User : %s" % user


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
@login_required
def ckeditor4():
    return render_template('ckeditor4.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title='Route Fail :(', str='Please... rewrite the path.', url='main_menu'), 404


@app.route('/product_main')
#@login_required
def product_main():
    row_object = Rows()
    return render_template('production_main.html', specific_list=None, object=row_object)


@app.route('/chartTable_main')
#@login_required
def chartTable_main():
    row_object = Rows()
    return render_template('chart_table_main.html', object=row_object)


@app.route('/insert_data', methods=["POST"])
def insert_data():
    print("POST - Insert Data :")
    date = datetime.datetime.today().strftime('%Y-%m-%d')

    # Input name value
    _week = request.values.getlist("insert_week")
    _model = request.values.getlist("insert_model")
    _sn = request.values.getlist("insert_sn")
    _header = request.values.getlist("insert_header")

    def find_model(collection, model):
        query = {
            'model': model
        }
        return collection.find_one(query)

    for i in range(0, len(_model)):
        try:
            db_object = MongodbConnection()
            rows_collection = db_object.db_conn(db_object.db_client(), 'model')
            _model_dic = find_model(rows_collection, _model[i])
            print(_model_dic)
        except Exception as e:
            db_object.db_close()
            print("DB_error : insert_model()", end=" : ")
            print(e)

        # Auto value
        _quality = 'N'
        _show = '1'
        auto_values = [_model_dic['_id'], _sn[i], _header[i], _week[i], _quality, _show]

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
            _product_id = query.insert_product_info(rows_collection, auto_values)
            print(_product_id)
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
        _note = ' '
        history_values = [_product_id, _date, _location, _state, _reason, _note]

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'history')
            query.insert_history(rows_collection, history_values)
        except Exception as e:
            db_object.db_close()
            print("DB_error : insert_history()", end=" : ")
            print(e)

    return redirect(url_for('product_main'))


@app.route('/state_change', methods=["POST"])
def state_change():
    def getStateFromReason(reason):
        # state_map = {
        #     '신규생산': '재고',
        #     '반납': '재고',
        #     '이동': '재고',
        #     '판매': '출고',
        #     '기증': '출고',
        #     '내수용': '출고',
        #     'A/S': '출고',
        #     '불량': '폐기'
        # }
        state_map = {
            '매입': '입고',
            '생산': '입고',
            '교체(입고)': '입고',
            '이월': '입고',
            '회수': '입고',
            '이동(입고)': '입고',
            '내수': '입고',
            '기타(입고)': '입고',

            '판매': '출고',
            '대여': '출고',
            '교체(출고)': '출고',
            '기증': '출고',
            '과제': '출고',
            '이동(출고)': '출고',
            '손상': '출고',
            '기타(출고)': '출고'
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
        _note = request.values.getlist("text")
        row_list = []
        print("GET State Change List : ",end="")
        print(_id, end=" ")
        print(_location, end=" ")
        print(_reason, end=" ")
        print(_note)
        for i in range(0, len(_id)):
            _state = getStateFromReason(_reason[i])
            row_list.append({'id': _id[i], 'location': _location[i],
                             'state': _state, 'reason': _reason[i], 'note': _note[i]})
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
            print("Change !! - ", end=" ")
            # print(_checked_id[i], end=" <-- ")
            print(row_list[j])
            # return find() -> Cursor Type
            # return insert() -> Object Type
            # return update() -> Dict Type

            p_id = row_list[j]['id']
            query.update_history(rows_collection, p_id)
            data = [row_list[j]['id'], date, row_list[j]['location'],
                    row_list[j]['state'], row_list[j]['reason'], row_list[j]['note']]
            query.insert_history(rows_collection, data)

    except Exception as e:
        print("DB_error : state_change()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return redirect(url_for('product_main'))


@app.route('/sendDetailModificationModalValue', methods=["POST"])
def sendDetailModificationModalValue():
    _sn = request.values.get("modify_sn")
    _week = request.values.get("modify_week")
    _header = request.values.get("modify_header")
    _product_id = request.values.get("modify_product_id")

    print("Get modification data : ", end="")
    print(type(_sn), end=" ")
    print(len(_sn), end=" ")
    print(_sn, end=" ")
    print(_week, end=" ")
    print(_header, end=" ")
    print(_product_id)

    modify_list = []
    if not _sn and _week and _header:
        print("Post value is Empty")
    if _sn:
        modify_list.append(_sn)
    else:
        modify_list.append(None)
    if _week:
        modify_list.append(_week)
    else:
        modify_list.append(None)
    if _header:
        modify_list.append(_header)
    else:
        modify_list.append(None)

    print("Modify_list : ")
    print(modify_list)

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')  # test db : Copy_of_product_info
        _DicTypeResult = query.update_product_info(rows_collection, _product_id, modify_list)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)

    print("Result : ")
    print(_DicTypeResult)

    _date = request.values.getlist('modify_date')
    _location = request.values.getlist('modify_location')
    _state = request.values.getlist('modify_state')
    _reason = request.values.getlist('modify_reason')
    _text = request.values.getlist("modify_text")
    history_list = []

    print("Get modification list data : ", end="")
    print(_date, end=" ")
    print(_location, end=" ")
    print(_state, end=" ")
    print(_reason, end=" ")
    print(_text)

    for i in range(0, len(_date)):
        history_list.append({'date': _date[i], 'location': _location[i], 'state': _state[i],
                             'reason': _reason[i], 'note': _text[i]})

    print("history List : ")
    for result in history_list:
        print(result)

    # 지금은 Index 방법으로 update를 하지만 추 후에는 ajax과정에서 id들도 같이 넘여주어서 id를 통해 update를 해야한다.

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'history')   # test db : Copy_of_history
        _CurTypeResult = rows_collection.find({'product_id': ObjectId(_product_id)})
    except Exception as e:
        print("DB_error : rows_collection.find()", end=" : ")
        print(e)

    print("Result : ")
    historyId = []
    for result in _CurTypeResult:
        historyId.append(result['_id'])
        print(result)

    print("History Id : ")
    print(historyId)

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'history')  # test db = Copy_of_history
        for i in range(0, len(historyId)):
            _DicTypeResult = query.update_modification_history(rows_collection, historyId[i], history_list[i])
            print("Modify !!")
            print(_DicTypeResult)
    except Exception as e:
        print("DB_error : update_modification_history()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    return redirect(url_for('product_main'))


# 생산 page
@app.route('/manufacture_main')
#@login_required
def manufacture_main():
    object_rows = Rows()
    return render_template('manufacture.html', specific_list=None, object=object_rows)


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
        _list = [_week, _model[i], int(_number[i]), date]
        _data_list.append(_list)
    print("Data List : ")
    for data in _data_list:
        print(data)
    try:
        db_object = MongodbConnection()
        for i in range(0, len(_data_list)):
            rows_collection = db_object.db_conn(db_object.db_client(), 'manufacture')
            _insert_id = query.insert_manufacture_info(rows_collection, _data_list[i])
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    return redirect(url_for('manufacture_main'))


'''


2019 - 03 - 10 개발 범위


'''


# Test Html pages
@app.route('/shipment_main')
@login_required
def shipment_main():
    row_object = Rows()
    return render_template('shipment_main.html', rows=None, object=row_object)


@app.route('/business_goal')
@login_required
def business_goal():
    return render_template('business_goal.html')


@app.route('/sales_performance')
@login_required
def sales_performance():
    return render_template('sales_performance.html')


@app.route('/partners_list')
@login_required
def partners_list():
    return render_template('partners_list.html')


@app.route('/receiving_inspection')
@login_required
def receiving_inspection():
    return render_template('receiving_inspection.html')


# 영업 page
@app.route('/sales_main')
@login_required
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

    return redirect(url_for('sales_main'))


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
        _insert_id = query.insert_partner_list(rows_collection, insert_data_list)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()
    return redirect(url_for('sales_main'))


# 통계 page
@app.route('/statistics_main')
@login_required
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/excel_table', methods=['POST'])
def excel_table():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                print('No file part')
                return redirect(url_for('insert_plan'))
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                print('No selected file')
                return redirect(url_for('insert_plan'))
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
    return redirect(url_for('product_main'))


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
