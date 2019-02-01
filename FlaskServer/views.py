from FlaskServer import app
import os
import random
import datetime
import pymongo
import pandas
from flask import render_template, request, current_app, make_response, url_for, redirect
from bson.objectid import ObjectId # For ObjectId to work

'''
ip = '211.106.106.183'
port = 27019
conn = pymongo.MongoClient(db_ip, db_port)
db = conn.get_database('ERP_testbk')
rows_collection = db.get_collection('test1')
print(type(rows_collection))
'''


class Mongodb_connection:
    _ip = '222.106.48.150'
    _port = 27019

    def __init__(self):
        # print(" ~~ ", sep = '\n')
        print("MongoDB connecting", end=' >> ')

    def db_client(self):
        return pymongo.MongoClient(Mongodb_connection._ip, Mongodb_connection._port)

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
def index():
    return render_template('index.html')


@app.route('/upload')
def ckeditor4():
    return render_template('ckeditor4.html')


@app.route('/')
def production_main():
    try:
        page = 'p_page'
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        now = date.split('-')
        for i in range(0, 3):
            now[i] = int(now[i])
        now = week_num(now[0], now[1], now[2])
    except Exception as e:
        print("Date_error : production_main()", end=" >> ")
        print(e)
    try:
        rows_list = search_query(now, now, page)
    except Exception as e:
        print("DB_error : production_main()", end=" >> ")
        print(e)
        return render_template('404.html'), 404
    return render_template('production_main.html', rows=rows_list, now_sdate=date, now_edate=date, shipment_modal_rows=shipment_modal_rows(), crows=custom_list())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def search_query(sdate, edate, page):
    # rows_list = list(rows_collection.find({'$and': [{'week': {'$gte': sdate}},{'week': {'$lte': edate}}]}))
    # query = {}
    # query["$and"] = [

    if page == 'p_page':
        coll = 'test1'
        query = {"$and": [
            {
                u"date.week": {
                    u"$gte": sdate
                }
            },
            {
                u"date.week": {
                    u"$lte": edate
                }
            },
            {
                u"detail.show": {
                    u"$eq": '1'
                }
            }
        ]}
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
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), coll)
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : search_query()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()
    if len(rows_list):
        new_list = []
        for i in range(0, len(rows_list)):
            if len(rows_list[i]['location']) == 1:
                lo_point = 0
            else:
                lo_point = -1
            if len(rows_list[i]['detail']['state']) == 1:
                st_point = 0
            else:
                st_point = -1
            new_list.append(
                {"model": rows_list[i]['model'], "sn": rows_list[i]['sn'], "week": rows_list[i]['date']['week'],
                 "location": rows_list[i]['location'][lo_point], "state": rows_list[i]['detail']['state'][st_point]})
        print(new_list)

        return new_list
    else:
        return rows_list

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

@app.route('/search', methods=['POST'])
def data_search():
    _page = request.values.get("page")
    _sdate = request.values.get("startDate")
    _edate = request.values.get("endDate")
    sdate = _sdate.split('-')
    edate = _edate.split('-')
    for i in range(0, 3):
        sdate[i] = int(sdate[i])
        edate[i] = int(edate[i])

    if int(sdate[0]) < int(edate[0]):
        rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]), _page)
    elif int(sdate[0]) == int(edate[0]):
        if int(sdate[1]) < int(edate[1]):
            rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]), _page)
        elif int(sdate[1]) == int(edate[1]):
            if int(sdate[2]) < int(edate[2]):
                rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]), _page)
            elif int(sdate[2]) == int(edate[2]):
                rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]), _page)
            else:
                print("Day Error")
                return redirect('/')
        else:
            print("month Error")
            return redirect('/')
    else:
        print("Year Error")
        return redirect('/')

    if _page == 'p_page':
        return render_template('production_main.html', rows=rows_list, now_sdate=_sdate, now_edate=_edate, shipment_modal_rows=shipment_modal_rows(), crows=custom_list())
    elif _page == 's_page':
        return render_template('shipment_main.html', rows=rows_list, now_sdate=_sdate, now_edate=_edate)
    else:
        print("POST hidden page value error ")

@app.route('/all_collection')
def all_collection_show():
    now = datetime.datetime.today().strftime('%Y-%m-%d')
    #query = {u"show": {u"$eq": '1'}}
    query = {u"detail.show": {u"$eq": "1"}}
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : all_collection_show()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()
    print(rows_list)
    new_list = []
    for i in range(0, len(rows_list)):
        new_list.append({"model": rows_list[i]['model'], "sn": rows_list[i]['sn'], "week": rows_list[i]['date']['week'], "location": rows_list[i]['location'][-1], "state": rows_list[i]['detail']['state'][-1]})
    print(new_list)
    return render_template('production_main.html', rows=new_list, now_sdate=now, now_edate=now, shipment_modal_rows=shipment_modal_rows(), crows=custom_list())


@app.route('/insert_plan')
def insert_plan():
    return render_template('plan_list.html', rows={})


def data_insert_query(collection, dataList):
    date = datetime.datetime.today().strftime('%Y%m%d') # Str type
    #query = {'model': dataList[0], 'sn': dataList[1], 'header': dataList[2], 'month': month, 'week': dataList[3], 'quality': dataList[4],
    #         'location': dataList[5], 'state': dataList[6], 'show': dataList[7], 'shipment': dataList[8], 'key': dataList[9]}
    #result = collection.insert_one(query)  # Insert_one objcet is not callable => List type X

    query = {'model': dataList[0], 'sn': dataList[1], 'location': [dataList[5]],
             'date': {'p_date': date, 'week': dataList[3], 's_date': [date]},
             'detail': {'header': dataList[2], 'quality': dataList[4], 'show': dataList[7],
                        'state': [dataList[6]]}}
    result = collection.insert(query)
    return result


@app.route('/insert_data', methods=["POST"])
def insert_data():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    now = date.split('-')
    for i in range(0, 3):
        now[i] = int(now[i])
    now = week_num(now[0], now[1], now[2])

    # Input value
    _model = request.values.get("model")
    _sn = request.values.get("sn")
    _header = request.values.get("header")
    print(_model, end=" ")
    print(_sn, end=" ")
    print(_header, end=" ")

    # Auto value
    _week = now
    _quality = 'N'
    _site = '대전'
    _state = '재고'        # 재고, 판매, 기증, 내수용, A/S입고, 폐기
    _show = '1'
    print(_week, end=" ")
    print(_quality, end=" ")
    print(_site, end=" ")
    print(_state, end=" ")
    print(_show, end=" ")
    # 0 ~ 7 : 8 value
    data_list = [_model, _sn, _header, _week, _quality, _site, _state, _show]

    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        data_insert_query(rows_collection, data_list)

    except Exception as e:
        print("DB_error : insert_data()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/')


@app.route('/shipment_data', methods=["POST"])
def shipment():
    if request.values.get("data_empty"):
        print("shipment POST data is empty")
        print(request.values.get("data_empty"))
        return redirect('/')
    elif not len(request.values.getlist("check_box")):
        print("shipment rows is empty")
        return redirect('/')
    else:
        try:
            _date = datetime.datetime.today().strftime('%Y%m%d')
            _checked_id = request.values.getlist("check_box")  # Checked the Object _id value
            _id = request.values.getlist("id")
            _location = request.values.getlist("location")
            _state = request.values.getlist("state")

            print(_checked_id, end=" ")
            print(_id, end=" ")
            print(_location, end=" ")
            print(_state)
            row_list = []
            for i in range(0, len(_id)):
                row_list.append({'id': _id[i], 'location': _location[i], 'state': _state[i]})
            print("POST row_list : ", end=" ")
            print(row_list)
        except Exception as e:
            print("POST_error : shipment()", end=" >> ")
            print(e)

        try:
            db_object = Mongodb_connection()
            for i in range(0, len(_checked_id)):
                for j in range(0, len(row_list)):
                    if _checked_id[i] == row_list[j]['id']:
                        print("Change !! ", end=" ")
                        print(_checked_id[i], end=" <-- ")
                        print(row_list[j])
                        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
                        # return find() -> Cursor Type
                        # return insert() -> Object Type
                        # return update() -> Dict Type
                        rows_collection.update({

                            '_id': ObjectId(row_list[j]['id'])
                        }, {
                            '$push': {'location': row_list[j]['location'], 'detail.state': row_list[j]['state']
                                      , 'date.s_date': _date}

                        })

        except Exception as e:
            print("DB_error : shipment()", end=" >> ")
            print(e)
        finally:
            db_object.db_close()

        return redirect('/')


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


@app.route('/insert_product')
def insert_product():
    return render_template('xxx.html')


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


'''



'''


@app.route('/shipment_main')
def shipment_main():
    try:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        sdate = datetime.datetime.today().strftime('%Y-01-01')
        '''
        now = date.split('-')
        for i in range(0, 3):
            now[i] = int(now[i])
        now = week_num(now[0], now[1], now[2])
        '''
    except Exception as e:
        print("Date_error : production_main()", end=" >> ")
        print(e)

    query = {u"_show": {u"$eq": '1'}}
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test2')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : all_collection_show()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return render_template('shipment_main.html', rows=rows_list, now_sdate=sdate, now_edate=date)

def custom_list():
    query = {"$and": [{u"detail.quality": {u"$eq": 'N'}}, {u"detail.show": {u"$eq": '1'}}]}
    print("c_list()")
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : ()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    if len(rows_list):
        sdata = []
        sloca = []
        sdate = []
        nlist = []
        id = []
        for i in range(0, len(rows_list)):
            id.append(rows_list[i]['_id'])
            sdata.append(rows_list[i]['detail']['state'])
            sloca.append(rows_list[i]['location'])
            sdate.append(rows_list[i]['date']['s_date'])
            nlist.append({'_id': id[i], 'sdata': sdata[i], 'sloca': sloca[i], 'sdate': sdate[i]})
        print(nlist)
        return nlist
    return rows_list

def shipment_modal_rows():
    # Must be a change quality value.
    query = {"$and": [{u"detail.quality": {u"$eq": 'N'}}, {u"detail.show": {u"$eq": '1'}}]}
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : all_collection_show()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    print(rows_list)

    if len(rows_list):
        new_list = []
        for i in range(0, len(rows_list)):
            if len(rows_list[i]['location']) == 1:
                lo_point = 0
            else:
                lo_point = -1
            if len(rows_list[i]['detail']['state']) == 1:
                st_point = 0
            else:
                st_point = -1
            if len(rows_list[i]['date']['s_date']) == 1:
                sd_point = 0
            else:
                sd_point = -1
            new_list.append({"_id": rows_list[i]['_id'], "model": rows_list[i]['model'], "sn": rows_list[i]['sn'],
                             "location": rows_list[i]['location'][lo_point],
                             "s_date": rows_list[i]['date']['s_date'][sd_point],
                             "state": rows_list[i]['detail']['state'][st_point]})
        print("new list", end=": ")
        print(new_list)
        return new_list
    else:
        return rows_list


@app.route('/insert_information', methods=["POST"])
def insert_information():
    if request.values.get("data_empty"):
        print("insert_information POST data is empty")
        print(request.values.get("data_empty"))
        return redirect('shipment_main')
    elif not len(request.values.getlist("check_box")):
        print("insert_information rows is empty")
        return redirect('shipment_main')
    else:
        try:
            _update_date = datetime.datetime.today().strftime('%Y-%m-%d')
            _checkbox = request.values.getlist("check_box") # Checked the Object _id value
            _contractNum = request.values.getlist("contractNum")
            _sum = request.values.getlist("sum")
            _deliveryDate = request.values.getlist("deliveryDate")
            _expectPayDate = request.values.getlist("expectPayDate")
            _realPayDate = request.values.getlist("realPayDate")

            print(_checkbox)
            print(_contractNum)
            print(_sum)
            print(_deliveryDate)
            print(_expectPayDate)
            print(_realPayDate)
            print(len(_checkbox))

        except Exception as e:
            print("POST_error : insert_insert_information()", end=" >> ")
            print(e)
        try:
            find_result = []
            rows = []
            db_object = Mongodb_connection()
            for i in range(0, len(_checkbox)):
                # return find() -> Cursor Type
                # return insert() -> Object Type
                # return update() -> Dict Type
                rows_collection = db_object.db_conn(db_object.db_client(), 'test2')
                find_result.append(rows_collection.find({

                    u"_id": {
                        u"$eq": ObjectId(_checkbox[i])
                    }

                }))
                print(find_result[i]) # Cursor Type
                rows += list(find_result[i])
            print(rows)
            for j in range(0, len(_checkbox)):
                rows_collection.update({

                    '_id': rows[j]['_id']
                }, {
                    '$set': {
                        '_contractNum': _contractNum[j],
                        '_sum': _sum[j],
                        '_deliveryDate': _deliveryDate[j],
                        '_expectPayDate': _expectPayDate[j],
                        '_realPayDate': _realPayDate[j]
                    }
                })

        except Exception as e:
            print("DB_error : shipment()", end=" >> ")
            print(e)
        finally:
            db_object.db_close()

        return redirect('/shipment_main')


@app.route('/detail_modal', methods=["POST"])
def detail_modal():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    now = date.split('-')
    for i in range(0, 3):
        now[i] = int(now[i])
    now = week_num(now[0], now[1], now[2])

    # Input value
    _model = request.values.get("model")
    _sn = request.values.get("sn")
    _header = request.values.get("header")
    print(_model, end=" ")
    print(_sn, end=" ")
    print(_header, end=" ")

    # Auto value
    _week = now
    _quality = 'N'
    _site = '대전'
    _state = '재고'        # 재고, 판매, 기증, 내수용, A/S입고, 폐기
    _show = '1'
    print(_week, end=" ")
    print(_quality, end=" ")
    print(_site, end=" ")
    print(_state, end=" ")
    print(_show, end=" ")
    # 0 ~ 7 : 8 value
    data_list = [_model, _sn, _header, _week, _quality, _site, _state, _show]

    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        data_insert_query(rows_collection, data_list)

    except Exception as e:
        print("DB_error : insert_data()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/all_collection')