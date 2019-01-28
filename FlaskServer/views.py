from FlaskServer import app
import os
import random
import datetime
import pymongo
import pandas
from flask import render_template, request, current_app, make_response, url_for, redirect

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
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    now = date.split('-')
    for i in range(0, 3):
        now[i] = int(now[i])
    now = week_num(now[0], now[1], now[2])
    try:
        rows_list = search_query(now, now)
    except Exception as e:
        print("DB_error : production_main()", end=" >> ")
        print(e)
        # return render_template('404.html'), 404

    modal_rows = {}

    return render_template('production_main.html', rows=rows_list, now_sdate=date, now_edate=date)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def search_query(sdate, edate):
    # rows_list = list(rows_collection.find({'$and': [{'week': {'$gte': sdate}},{'week': {'$lte': edate}}]}))
    query = {}
    query["$and"] = [
        {
            u"week": {
                u"$gte": sdate
            }
        },
        {
            u"week": {
                u"$lte": edate
            }
        }
    ]
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except Exception as e:
        print("DB_error : search_query()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()
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
    _sdate = request.values.get("startDate")
    _edate = request.values.get("endDate")
    sdate = _sdate.split('-')
    edate = _edate.split('-')
    for i in range(0, 3):
        sdate[i] = int(sdate[i])
        edate[i] = int(edate[i])

    if int(sdate[0]) < int(edate[0]):
        list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]))
    elif int(sdate[0]) == int(edate[0]):
        if int(sdate[1]) < int(edate[1]):
            list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]))
        elif int(sdate[1]) == int(edate[1]):
            if int(sdate[2]) < int(edate[2]):
                list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]))
            elif int(sdate[2]) == int(edate[2]):
                list = search_query(week_num(sdate[0], sdate[1], sdate[2]), week_num(edate[0], edate[1], edate[2]))
            else:
                print("Day Error")
                return redirect('/')
        else:
            print("month Error")
            return redirect('/')
    else:
        print("Year Error")
        return redirect('/')

    return render_template('production_main.html', rows=list, now_sdate=_sdate, now_edate=_edate)


@app.route('/all_collection')
def all_collection_show():
    now = datetime.datetime.today().strftime('%Y-%m-%d')
    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        rows_list = list(rows_collection.find())  # cursor type -> list type
    except Exception as e:
        print("DB_error : all_collection_show()")
        print(e)
    finally:
        db_object.db_close()
        # print(rows_list)
        print(rows_list[0])
    return render_template('production_main.html', rows=rows_list, now_sdate=now, now_edate=now)


@app.route('/insert_plan')
def insert_plan():
    return render_template('plan_list.html', rows={})


def data_insert_query(collection, list):
    query = {'model': list[0], 'sn': list[1], 'header': list[2], 'week': list[3], 'quality': list[4],
             'location': list[5], 'csState': list[6], 'shipment': list[7], 'key': list[8]}
    result = collection.insert_one(query)  # Insert_one objcet is not callable => List type X
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
    _date = now
    _quality = 'N'
    _site = '대전'
    _csState = 'N'
    _show = '1'
    _shipment = 'N'
    _key = _sn + str(_show)
    print(_date, end=" ")
    print(_quality, end=" ")
    print(_site, end=" ")
    print(_csState, end=" ")
    print(_show, end=" ")
    print(_shipment, end=" ")
    print(_key)

    data_list = [_model, _sn, _header, _date, _quality, _site, _csState, _show, _shipment, _key]

    try:
        db_object = Mongodb_connection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        data_insert_query(rows_collection, data_list)

    except Exception as e:
        print("DB_error : insert_data()")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/')


@app.route('/shipment_data', methods=["POST"])
def shipment():


    data = request.values.get("key[]")
    data2 = request.values.get("key[0]")
    print (data)
    print (data2)

   #for i in range(0,len(datas)):
    #    print(str(i) + " " + str(datas[i]))


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
        print(" Excel_table() Error ")
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


@app.route('/shipment_main')
def shipment_main():
    return render_template('shipment_main.html')
