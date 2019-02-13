from FlaskServer import app
import os
import random
import datetime
import pymongo
import pandas
from flask import render_template, request, current_app, make_response, url_for, redirect
from bson.objectid import ObjectId  # For ObjectId to work
from collections import OrderedDict

'''
ip = '211.106.106.183'
port = 27019
conn = pymongo.MongoClient(db_ip, db_port)
db = conn.get_database('ERP_testbk')
rows_collection = db.get_collection('test1')
print(type(rows_collection))
'''


class Mongodb_connection:

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
        self._DB_object = Mongodb_connection()

    # def production_main_list(self):

    def main_table_rows(self):
        result_rows = []
        query = {"show": {'$eq': '1'}}
        try:
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'history')
            rows_list = list(rows_collection.find(query))  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.model()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        id_list = []
        loca_list = []
        sta_list = []
        date_list = []
        for row in rows_list:
            id_list.append(row['product_id'])
            loca_list.append(row['location'])
            sta_list.append(row['state'])
            date_list.append(row['date'])
        print(id_list)
        print(loca_list)
        print(sta_list)
        print(date_list)

        we_list = []
        sn_list = []
        mo_list = []
        rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'product_info')
        for id in id_list:
            query = {"_id": {'$eq': ObjectId(id)}}
            row = list(rows_collection.find(query))  # cursor type -> list type
            print(row)
            print(row[0])
            print(row[0]['week'])
            we_list.append(row[0]['week'])
            sn_list.append(row[0]['sn'])
            mid = row[0]['model_id']

            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'model')
            query = {"_id": {'$eq': ObjectId(mid)}}
            row = list(rows_collection.find(query))  # cursor type -> list type
            mo_list.append(row[0]['model'])

        print(we_list)
        print(sn_list)
        print(mo_list)
        for i in range(0, len(loca_list)):
            res = mo_list[i] + sn_list[i] + we_list[i] + loca_list[i] + sta_list[i]
            result_rows.append(res)
        self._DB_object.db_close()

        print(result_rows)



        rows_list = [{'model': 'indy', 'sn': 'D2313', 'week': '1908', 'location': '대전', 'state': '입고'},
                     {'model': 'opty', 'sn': 'D1293', 'week': '1908', 'location': '대전', 'state': '입고'},
                     {'model': 'step', 'sn': 'D6643', 'week': '1908', 'location': '대전', 'state': '입고'}]

        return rows_list

    def production_main_model(self):
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

    def date(self):
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        return date


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


'''
query = {u"_id": {u"$eq": ObjectId('5c569b1e0f055d57e83e0dda') } }
query2 = {u"user_id": {u"$eq": '5c569b1e0f055d57e83e0dda' } }
query2 = {u"product_id": {u"$eq": ObjectId('5c5707d7cbf63c5290057130') }}

'''


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    object = Rows()
    a = object.production_main_all_list()
    print(a)
    print(type(a))
    print(a[0]['_id'])
    return render_template('test.html', aaa=a, object=object)


@app.route('/upload')
def ckeditor4():
    return render_template('ckeditor4.html')


@app.route('/')
def production_main():
    row_object = Rows()
    row_object.main_table_rows()

    return render_template('production_main.html', date_rows='', object=row_object)


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
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), collection_of_product_info)
        rows_list = list(rows_collection.find(product_info_query))  # cursor type -> list type
        list_of_model_id = []
        list_of_history_id = []
        for row in rows_list:
            list_of_model_id.append(row['model_id'])
            list_of_history_id.append(row['history_id'])
        # print("list_of_model_id : ", end="")
        # print(list_of_model_id)

        rows_collection = db_object.db_conn(db_object.db_client(), collection_of_model)
        list_of_model = []
        for model_id in list_of_model_id:
            model_query = {u"_id": {u"$eq": ObjectId(model_id)}}
            list_of_model.extend(list(rows_collection.find(model_query)))  # cursor type -> list type

        rows_collection = db_object.db_conn(db_object.db_client(), collection_of_history)
        list_of_history = []
        for history_id in list_of_history_id:
            history_query = {u"_id": {u"$eq": ObjectId(history_id)}}
            list_of_history.extend(list(rows_collection.find(history_query)))  # cursor type -> list type
        # print(map_list)
        result_list = [rows_list, list_of_model, list_of_history]
        # print(result_list)
    except Exception as e:
        print("DB_error : search_query()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return result_list


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
            rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]),
                                     _page)
        elif int(sdate[1]) == int(edate[1]):
            if int(sdate[2]) < int(edate[2]):
                rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]),
                                         _page)
            elif int(sdate[2]) == int(edate[2]):
                rows_list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]),
                                         _page)
            else:
                print("Day Error")
                return redirect('/')
        else:
            print("month Error")
            return redirect('/')
    else:
        print("Year Error")
        return redirect('/')

    row_object = Rows()

    if _page == 'p_page':
        print(rows_list)
        return render_template('production_main.html', date_rows=rows_list, object=row_object)
    # Not use
    elif _page == 's_page':
        return render_template('shipment_main.html', rows=rows_list, now_sdate=_sdate, now_edate=_edate)
    else:
        print("POST hidden page value error ")


@app.route('/all_collection')
def all_collection_show():
    # Not use
    '''
    query = {u"show": {u"$eq": "1"}}
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'product')
        rows_list = list(rows_collection.find())  # cursor type -> list type
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
        new_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : all_collection_show()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    rows_list = rows_list + new_list
    print(rows_list)

    for row in rows_list:
        for key, val in row.items():
            if key == '_id':
                print("%s    %s " % (key, val))

    rows_object = Rows()


    return render_template('production_main.html', date_rows=rows_list, object=rows_object)
    '''
    return render_template('404.html'), 404


@app.route('/insert_plan')
def insert_plan():
    return render_template('plan_list.html', rows={})


def insert_model(collection, model):
    # Add Meta Data Later.
    query = {'model': model}
    return collection.insert(query)  # Return value is ObjectId


def insert_history(collection, args_list):
    query = {'product_id': args_list[0],
             'index': '0',
             'show': '1',
             'date': args_list[1],
             'location': args_list[2],
             'state': args_list[3],
             'reason': args_list[4]}
    return collection.insert(query)


def insert_product_info(collection, args_list):
    query = {'model_id': args_list[0], 'sn': args_list[1], 'header': args_list[2],
             'week': args_list[3], 'quality': args_list[4], 'show': args_list[5]}

    return collection.insert(query)  # Return value is ObjectId


@app.route('/insert_data', methods=["POST"])
def insert_data():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    now = date.split('-')
    for i in range(0, 3):
        now[i] = int(now[i])
    now = week_num(now[0], now[1], now[2])

    # Input name value
    _model = request.values.get("model")
    _sn = request.values.get("sn")
    _header = request.values.get("header")

    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'model')
        _model_id = str(insert_model(rows_collection, _model))
    except Exception as e:
        db_object.db_close()
        print("DB_error : insert_model()", end=" : ")
        print(e)

    # Auto value
    _week = now
    _quality = 'N'
    _show = '1'
    auto_values = [_model_id, _sn, _header, _week, _quality, _show]

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
    _state = '입고'   # 입고, 출고, 이동
    _reason = '재고'  # 재고, 판매, 기증, 내수용, A/S입고, 폐기
    history_values = [_product_id, _date, _location, _state, _reason]

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'history')
        insert_history(rows_collection, history_values)
    except Exception as e:
        db_object.db_close()
        print("DB_error : insert_history()", end=" : ")
        print(e)

    return redirect('/')


@app.route('/state_change', methods=["POST"])
def state_change():
    if request.values.get("data_empty"):
        print("state_change POST data is empty")
        print(request.values.get("data_empty"))
        return redirect('/')
    elif not len(request.values.getlist("check_box")):
        print("state_change rows is empty")
        return redirect('/')
    else:
        try:
            date = datetime.datetime.today().strftime('%Y-%m-%d')
            _date = {'date': date}
            _checked_id = request.values.getlist("check_box")  # Checked the Object _id value
            _id = request.values.getlist("id")
            _location = request.values.getlist("location")
            _state = request.values.getlist("states")
            row_list = []
            for i in range(0, len(_id)):
                row_list.append({'id': _id[i], 'location': _location[i], 'state': _state[i]})
        except Exception as e:
            print("POST_error : state_change()", end=" >> ")
            print(e)
        else:
            print(_checked_id, end=" ")
            print(_id, end=" ")
            print(_location, end=" ")
            print(_state)
            print("POST row_list : ", end=" ")
            print(row_list)
        try:
            db_object = Mongodb_connection()
            for i in range(0, len(_checked_id)):
                for j in range(0, len(row_list)):
                    if _checked_id[i] == row_list[j]['id']:
                        print("Change !! ", end=" ")
                        print(_checked_id[i], end=" <-- ")
                        print(row_list[j])
                        rows_collection = db_object.db_conn(db_object.db_client(), 'history')
                        print("Test :", end="  ")
                        print(row_list[j].items())
                        # return find() -> Cursor Type
                        # return insert() -> Object Type
                        # return update() -> Dict Type
                        '''
                        rows_collection.update({
                            '_id': ObjectId(row_list[j]['id'])
                        }, {
                            '$push': {'location': row_list[j]['location'], 'state': row_list[j]['state'],
                                      'updated_date': _date}
                        })
                        '''
                        print("** : ", end=" ")
                        print({row_list[j]})
                        rows_collection.update({
                            '_id': ObjectId(row_list[j]['id'])
                        }, {
                            'location_history': {'$push': {'0': row_list[j]['location']}},
                            'state_history': {'$push': {'0': row_list[j]['state']}},
                            'date_history': {'$push': {'0': _date}}
                        })
        except Exception as e:
            print("DB_error : state_change()", end=" >> ")
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

# Not use 

'''


@app.route('/shipment_main')
def shipment_main():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    sdate = datetime.datetime.today().strftime('%Y-%m-01')

    row_object = Rows()

    # Temporarily
    rows = [{'_model': 'Indy', '_sn': 'D321321', '_product_week': '1907', '_outDate': '2019-02-11'}]

    return render_template('shipment_main.html', object=row_object, rows=rows, now_sdate=sdate, now_edate=date)


@app.route('/business_goal')
def business_goal():
    return render_template('business_goal.html')


@app.route('/sales_performance')
def sales_performance():
    return render_template('sales_performance.html')


@app.route('/partners_list')
def partners_list():
    return render_template('partners_list.html')


@app.route('/receiving_inspection')
def receiving_inspection():
    return render_template('receiving_inspection.html')


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
            _checkbox = request.values.getlist("check_box")  # Checked the Object _id value
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
                print(find_result[i])  # Cursor Type
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
            print("DB_error : state_change()", end=" >> ")
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
    _state = '재고'  # 재고, 판매, 기증, 내수용, A/S입고, 폐기
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
        # insert_model(rows_collection, data_list)

    except Exception as e:
        print("DB_error : insert_data()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/all_collection')
