from FlaskServer.pymongo import MongodbConnection
from flask import request, render_template, jsonify
from bson.objectid import ObjectId
from FlaskServer import app

# 재고 관리
from FlaskServer.rowObejct import Rows
from FlaskServer.rowObejct import week_num
import FlaskServer.query as query


@app.route('/filtering', methods=["POST"])
def filtering():
    _filter = request.values.get('filter')
    _sub_filter = request.values.get('sub_filter')
    _sDate = request.values.get('sDate')
    _eDate = request.values.get('eDate')

    print("Filtering1 Get value : ")
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


@app.route('/filtering2', methods=["GET"])  # Ajax ver
def filtering2():
    _filter = request.args.get('filter')
    _sub_filter = request.args.get('sub_filter')
    _sDate = request.args.get('sDate')
    _eDate = request.args.get('eDate')
    _flag = request.args.get('second_filter_flag')
    if _flag == 'true':
        _second_filter = request.args.get('second_filter')
        _second_sub_filter = request.args.get('second_sub_filter')
        print("Get Sub_filter Value : ", end="")
        print(_second_filter, end=" ")
        print(_second_sub_filter)

    print("Filtering2 Get value : ", end="")
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

    # Date Value Check
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
        query = {"$and": [{"product_id": {'$eq': ObjectId(str(row['_id']))}}, {'show': {'$eq': '1'}}]}
        history_rows.extend(list(history_coll.find(query)))  # cursor type -> list type

    print("\nDate match rows :")
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
        del lis['_id']
        del lis['model_id']
        lis['product_id'] = str(lis['product_id'])
        print(lis)

    def dynamic_filter(dic):
        result = []
        print("Filtering Start")
        for key, val in dic.items():
            print(key, end=" ")
            print(val)

            if key == '전체':
                continue
            elif key == '모델':
                result.append({'model': val})
            elif key == '위치':
                result.append({'location': val})
            elif key == '상태':
                result.append({'state': val})
            # elif key == '모델':
            #     result['model'] = val
            # elif key == '위치':
            #     result['location'] = val
            # elif key == '상태':
            #     result['state'] = val
        return result

    if _flag == 'false':
        filter_dic = {_filter: _sub_filter}
    else:
        filter_dic = {_filter: _sub_filter, _second_filter: _second_sub_filter}
    print(filter_dic)

    result_list = merge_list.copy()
    after_filtering_list = []
    for item in dynamic_filter(filter_dic):
        print("\nFiltering : ", end="")
        print(item)
        if 'model' in item:
            print("> Model Filtering")
            for idx, merge_row in enumerate(result_list):
                if merge_row.get('model') == item['model']:
                    print(idx, merge_row)
                    after_filtering_list.append(merge_row)
                else:
                    print("Delete : ", end='')
                    print(idx, merge_row)

        if 'location' in item:
            print(">> Location Filtering")
            for idx, merge_row in enumerate(result_list):
                if merge_row.get('location') == item['location']:
                    print(idx, merge_row)
                    after_filtering_list.append(merge_row)
                else:
                    print("Delete : ", end='')
                    print(idx, merge_row)

        if 'state' in item:
            print(">>> State Filtering")
            for idx, merge_row in enumerate(result_list):
                if merge_row.get('state') == item['state']:
                    print(idx, merge_row)
                    after_filtering_list.append(merge_row)
                else:
                    print("Delete : ", end='')
                    print(idx, merge_row)

        result_list.clear()
        result_list = after_filtering_list.copy()
        after_filtering_list.clear()

    print("\nAfter Filtering")
    if not result_list:
        print("After filtering . . . List is Empty")
    else:
        for lis in result_list:
            print(lis)

    return jsonify(result_list)

    #
    # # Filtering Start
    # if _filter == '전체':
    #     m_value = None
    #     l_value = None
    #     s_value = None
    # elif _filter == '모델':
    #     m_value = _sub_filter
    #     l_value = None
    #     s_value = None
    # elif _filter == '위치':
    #     m_value = None
    #     l_value = _sub_filter
    #     s_value = None
    # elif _filter == '상태':
    #     m_value = None
    #     l_value = None
    #     s_value = _sub_filter
    # else:
    #     m_value = _sub_filter
    #     l_value = _sub_filter
    #     s_value = _sub_filter
    #
    # _filter_dic = {'model': m_value, 'location': l_value, 'state': s_value}
    #
    # print(_filter_dic)
    #
    # first_filtering_list = []
    # second_filtering_list = []
    # third_filtering_list = []
    # print("\n> Model Filtering")
    # if _filter_dic['model'] is not None:
    #     for idx, merge_row in enumerate(merge_list):
    #         if merge_row.get('model') == _filter_dic['model']:
    #             print(idx, merge_row)
    #             first_filtering_list.append(merge_row)
    #         else:
    #             print("Delete : ", end='')
    #             print(idx, merge_row)
    # else:
    #     first_filtering_list = merge_list
    #
    # print(">> Location Filtering")
    # if _filter_dic['location'] is not None:
    #     for idx, merge_row in enumerate(first_filtering_list):
    #         if merge_row.get('location') == _filter_dic['location']:
    #             print(idx, merge_row)
    #             second_filtering_list.append(merge_row)
    #         else:
    #             print("Delete : ", end='')
    #             print(idx, merge_row)
    # else:
    #     second_filtering_list = first_filtering_list
    #
    # print(">>> State Filtering")
    # if _filter_dic['state'] is not None:
    #     for idx, merge_row in enumerate(second_filtering_list):
    #         if merge_row.get('state') == _filter_dic['state']:
    #             print(idx, merge_row)
    #             third_filtering_list.append(merge_row)
    #         else:
    #             print("Delete : ", end='')
    #             print(idx, merge_row)
    # else:
    #     third_filtering_list = second_filtering_list
    #
    # print("After Filtering")
    # if not third_filtering_list:
    #     print("After filtering . . . List is Empty")
    # else:
    #     for lis in third_filtering_list:
    #         print(lis)
    #
    # return jsonify(third_filtering_list)
    #

@app.route('/getDetailTable')
def getDetailTable():
    _id = request.args.get('product_info_id')
    print("Detail Ajax : ", end='')
    print(_id)
    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'history')
        history_list = list(query.find_history_all_item(rows_collection, _id))
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    print(history_list)

    product_info_list = []
    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
        product_info_dic = query.find_production_info_item(rows_collection, _id)
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    finally:
        db_object.db_close()
    print(product_info_dic)

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'model')
        model_dic = rows_collection.find_one({'_id': product_info_dic['model_id']})
    except Exception as e:
        print("DB_error : insert_manufacture()", end=" : ")
        print(e)
    print(model_dic)

    print("Product info : ", end='')
    merge_dic = {}
    merge_dic.update(product_info_dic)
    merge_dic.pop('model_id')
    merge_dic['model'] = model_dic['model']
    product_info_list.append(merge_dic)
    print(product_info_list)

    for result in history_list:
        product_info_list.append(result)

    return jsonify(product_info_list)


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
            product_dic = query.find_production_info_item(rows_collection, _id)
            product_dic['model_id'] = str(product_dic['model_id'])
        except Exception as e:
            print("DB_error : getStateChangeTable() - product_info", end=" : ")
            print(e)

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'model')
            model_dic = rows_collection.find_one({'_id': ObjectId(product_dic['model_id'])}, {'_id': False})
        except Exception as e:
            print("DB_error : getStateChangeTable() - product_info", end=" : ")
            print(e)

        try:
            rows_collection = db_object.db_conn(db_object.db_client(), 'history')
            history_dic = query.find_history_item(rows_collection, _id)
            history_dic['product_id'] = str(history_dic['product_id'])
        except Exception as e:
            print("DB_error : getStateChangeTable() - history", end=" : ")
            print(e)
        finally:
            db_object.db_close()

        print("Product list : ")
        print(product_dic)
        print("Model list : ")
        print(model_dic)
        print("History list : ")
        print(history_dic)

        result_dic = {}
        result_dic.update(product_dic)
        result_dic.update(model_dic)
        result_dic.update(history_dic)
        result_list.append(result_dic)

    print("Result list : ")
    print(result_list)

    return jsonify(result_list)


@app.route("/getManufactureDB")
def getManufactureDB():
    _week = request.args.get("week")
    _model = request.args.get("model")
    _index = int(request.args.get("index"))
    print("Get ManufactureDB Ajax : ", end="")
    print(_week, end=" ")
    print(_model, end=" ")
    print(_index)

    def find_manufacture_count(collection, week, model):
        _query = {
            u"week": {
                u"$eq": week
            },
            u"model": {
                u"$eq": model
            }
        }
        _pipeline = [
            {
                "$match": {"week": {"$eq": week}, "model": {"$eq": model}}
            }, {
                "$group": {"_id": "$model", "number": {"$sum": "$number"}}
            }
        ]
        #return collection.find(_query)
        return collection.aggregate(_pipeline)

    try:
        db_object = MongodbConnection()
        rows_collection = db_object.db_conn(db_object.db_client(), 'manufacture')
        numberOfManufacture = list(find_manufacture_count(rows_collection, _week, _model))
    except Exception as e:
        print("DB_error : getManufactureDB() - manufacture", end=" : ")
        print(e)

    print(numberOfManufacture)

    if not numberOfManufacture:
        numberOfManufacture = 0
    else:
        numberOfManufacture = numberOfManufacture[0]['number']

    print("Number of result : ", end="")
    print(numberOfManufacture)

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'model')
        model_dic = rows_collection.find_one({'model': _model})
    except Exception as e:
        print("DB_error : getManufactureDB() - product", end=" : ")
        print(e)

    print(model_dic['_id'])

    def find_product_count(collection, week, model_id):
        _query = {
            u"week": week,
            u"model_id": model_id
        }
        return collection.find(_query).count()

    try:
        rows_collection = db_object.db_conn(db_object.db_client(), 'product_info')
        numberOfProduct = find_product_count(rows_collection, _week, model_dic['_id'])
    except Exception as e:
        print("DB_error : getManufactureDB() - product", end=" : ")
        print(e)
    finally:
        db_object.db_close()

    print("numberOfProduct : ", end="")
    print(numberOfProduct)

    result = {"number": numberOfManufacture - numberOfProduct, "index": _index}
    print("Result : ", end="")
    print(result)



    return jsonify(result)


# 생산 관리
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
            count_dic[_model_list[i]] = query.find_number_of_model(rows_collection, _model_list[i], _week_list[i])
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




# 영업


# 통계