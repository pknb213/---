from FlaskServer import app
import os
import random
import datetime
import pymongo
from flask import render_template, request, current_app, make_response, url_for, redirect

port = 27019
conn = pymongo.MongoClient('211.106.106.186', port)

db = conn.get_database('ERP_test')
rows_collection = db.get_collection('test1')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload')
def ckeditor4():
    return render_template('ckeditor4.html')

@app.route('/')
def production_main():
    rows = rows_collection.find()
    rows_list = list(rows)
    return render_template('production_main.html', rows=rows_list)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

def week_num(year,mon,day):
    n = datetime.datetime(year,mon,day)
    print(n) # calender date
    n = n.isocalendar()
    print(n) # week num
    n = list(n) # casting tuple -> list
    year = str(year) # casting int -> str
    result = year[2:4] + str(n[1]) # slice 2~4 char + week num
    return result

def search_query(sdate, edate):
    rows = rows_collection.find({'$and': [{'week': {'$gte': sdate}},{'week': {'$lte': edate}}]})
    rows_list = list(rows)
    return rows_list

@app.route('/search', methods=['POST'])
def data_search():
    sdate = request.values.get("startDate")
    edate = request.values.get("endDate")
    sdate = sdate.split('-')
    edate = edate.split('-')
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
        else:
            print("month Error")
    else:
        print("Year Error")

    return render_template('production_main.html', rows=list)

@app.route('/all_collection')
def all_collection_show():
    rows = rows_collection.find()
    rows_list = list(rows)
    return render_template('production_main.html', rows=rows_list)

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
