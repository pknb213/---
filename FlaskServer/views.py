from FlaskServer import app
import os
import random
import datetime
import pymongo
import pandas
from werkzeug.utils import secure_filename
from flask import render_template, request, current_app, make_response, url_for, redirect

db_ip = '192.168.0.3'
db_port = 27017
'''
ip = '211.106.106.183'
port = 27019
conn = pymongo.MongoClient(db_ip, db_port)
db = conn.get_database('ERP_test')
rows_collection = db.get_collection('test1')
print(type(rows_collection))
'''
query = {}

class Mongodb_connection:
    def __init__(self):
        # print(" ~~ ", sep = '\n')
        print("MongoDB connecting", end=' >> ')

    def db_client(self, ip, port):
        return pymongo.MongoClient(ip, port)

    def db_conn(self, client, coll):
        db = client.get_database('ERP_test')
        print("Connect", end=' >> ')
        return db.get_collection(coll)

    def db_close(self, ip, port):
        print("Disconnect")
        return self.db_client(ip, port).close()

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
    now = datetime.datetime.today().strftime('%Y-%m-%d')
    try:
        rows_list = search_query(now, now)
    except:
        print("Db_error : production_main()")
    return render_template('production_main.html', rows=rows_list, now_sdate=now, now_edate=now)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

def week_num(year,mon,day):
    n = datetime.datetime(year,mon,day)
    #print(n) # calender date
    n = n.isocalendar()
    #print(n) # week num
    n = list(n) # casting tuple -> list
    year = str(year) # casting int -> str
    result = year[2:4] + str(n[1]) # slice 2~4 char + week num
    return result

def search_query(sdate, edate):
    #rows_list = list(rows_collection.find({'$and': [{'week': {'$gte': sdate}},{'week': {'$lte': edate}}]}))

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
        rows_collection = db_object.db_conn(db_object.db_client(db_ip, db_port), 'test1')
        rows_list = list(rows_collection.find(query))  # cursor type -> list type
    except:
        print("Db_error : search_query()")
    finally:
        db_object.db_close(db_ip, db_port)
    return rows_list

@app.route('/search', methods=['POST'])
def data_search():
    _sdate = request.values.get("startDate")
    _edate = request.values.get("endDate")
    sdate = _sdate.split('-')
    edate = _edate.split('-')
    for i in range(0,3):
        sdate[i] = int(sdate[i])
        edate[i] = int(edate[i])

    if int(sdate[0]) < int(edate[0]):
        list = search_query(week_num(sdate[0], sdate[1], sdate[2]),week_num(edate[0], edate[1], edate[2]))
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
        rows_collection = db_object.db_conn(db_object.db_client(db_ip, db_port), 'test1')
        rows_list = list(rows_collection.find())   # cursor type -> list type
    except:
        print("Db_error : all_collection_show()")
    finally:
        db_object.db_close(db_ip, db_port)
        #print(rows_list)
        print(rows_list[0])
    return render_template('production_main.html', rows=rows_list, now_sdate=now, now_edate=now)

@app.route('/insert_plan')
def insert_plan():

    return render_template('plan_list.html', rows = {1,2,3,4})

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/excel_table', methods=['GET','POST'])
def excel_table():
    '''
    if request.method == 'POST':
        if 'file' not in request.files:
            print("NO")
        print(request.files['file'])
        f = request.files['file']
        data_xls = pandas.read_excel(f)
    '''

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
            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

            #df = pandas.read_excel('abc.xlsx', sheet_name='sheet1', engine='xlrd')
            df = pandas.read_excel('./FlaskServer/static/excel/생산계획.xlsx', sheet_name='sheet1', engine='xlrd')
            print(df.head())
            #return df.to_html()

            print(df)
            print(type(df))

            print(df['월'])
            rows_list = []
            '''
            rows_list.append(list(df['월']))
            rows_list.append(list(df['주차']))
            rows_list.append(list(df['모델코드']))
            rows_list.append(list(df['모델명']))
            rows_list.append(list(df['수량']))
            print (rows_list)
            for i in rows_list:
                print(i)
            print(rows_list[1])
            '''

            rows_list.append(list(df.loc[0]))
            rows_list.append(list(df.loc[1]))
            rows_list.append(list(df.loc[2]))
            rows_list.append(list(df.loc[3]))
            rows_list.append(list(df.loc[4]))


            return render_template('plan_list.html', rows=rows_list)
            #return redirect(url_for('insert_plan', filename=file.filename))

    #return df.to_html()
    #return make_read_excel()
    #return render_template('plan_list.html', rows=rows_list)

@app.route('/insert_product')
def insert_product():
    return render_template('insert_popup.html')

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