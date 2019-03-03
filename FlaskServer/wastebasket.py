# Not use

# 기본적인 pymongo 접근 방법
"""
ip = '211.106.106.183'
port = 27019
conn = pymongo.MongoClient(db_ip, db_port)
db = conn.get_database('ERP_testbk')
rows_collection = db.get_collection('test1')
print(type(rows_collection))
"""

# 예전 필터링 함수
"""
@app.route('/filtering2', methods=["POST"])
def filtering2():
    _model_filter = request.values.get('model_filter')
    _location_filter = request.values.get('location_filter')
    _state_filter = request.values.get('state_filter')
    _sDate = request.values.get('sDate')
    _eDate = request.values.get('eDate')

    print("Get value : ")
    print(_model_filter + ' ' + _location_filter + ' ' + _state_filter + ' ' + _sDate + ' ' + _eDate)

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

    if _model_filter == '모델':
        m_value = None
    else:
        m_value = _model_filter

    if _location_filter == '위치':
        l_value = None
    else:
        l_value = _location_filter

    if _state_filter == '상태':
        s_value = None
    else:
        s_value = _state_filter

    _filter = {'model': m_value, 'location': l_value, 'state': s_value}

    print(_filter)

    first_filtering_list = []
    second_filtering_list = []
    third_filtering_list = []
    print("> Model Filtering")
    if _filter['model'] is not None:
        for idx, merge_row in enumerate(merge_list):
            if merge_row.get('model') == _filter['model']:
                print(idx, merge_row)
                first_filtering_list.append(merge_row)
            else:
                print("Delete : ", end='')
                print(idx, merge_row)
    else:
        first_filtering_list = merge_list

    print(">> Location Filtering")
    if _filter['location'] is not None:
        for idx, merge_row in enumerate(first_filtering_list):
            if merge_row.get('location') == _filter['location']:
                print(idx, merge_row)
                second_filtering_list.append(merge_row)
            else:
                print("Delete : ", end='')
                print(idx, merge_row)
    else:
        second_filtering_list = first_filtering_list

    print(">>> State Filtering")
    if _filter['state'] is not None:
        for idx, merge_row in enumerate(second_filtering_list):
            if merge_row.get('state') == _filter['state']:
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
    print(third_filtering_list)
    row_object = Rows()

    return render_template('production_main.html', date_rows=third_filtering_list, object=row_object)
"""

#  기본적인 Ajax 테스트 함수
"""
@app.route('/ajax')
def ajaxTest():
    print("ajax test....")
    _name = request.args.get("name")
    print(_name)
    print(type(_name))
    testJson = {"key": _name}
    print(testJson)
    testJson = jsonify(testJson)
    print(type(testJson))
    print(testJson)
    return testJson
"""

# 예전 날짜 조회 함수
"""
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
        print("Date search : ", end="")
        print(rows_list)
        return render_template('production_main.html', date_rows=rows_list, object=row_object)
    # Not use
    elif _page == 's_page':
        return render_template('shipment_main.html', rows=rows_list, now_sdate=_sdate, now_edate=_edate)
    else:
        print("POST hidden page value error ")
"""

# 전체 조회 함수
'''
@app.route('/all_collection')
def all_collection_show():
    # Not use

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


    return render_template('production_main.html', specific_list=rows_list, object=rows_object)

    return render_template('404.html'), 404
'''

# 생산계획 등록 모달 함수
"""
@app.route('/insert_plan')
def insert_plan():
    return render_template('plan_list.html', rows={})

"""

# 옛날 만든 함수
"""
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
        db_object = MongodbConnection()
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
        db_object = MongodbConnection()
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
            db_object = MongodbConnection()
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
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'test1')
        # insert_model(rows_collection, data_list)

    except Exception as e:
        print("DB_error : insert_data()", end=" >> ")
        print(e)
    finally:
        db_object.db_close()

    return redirect('/all_collection')
"""