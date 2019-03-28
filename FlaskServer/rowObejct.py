from flask import render_template
from FlaskServer.pymongo import MongodbConnection
from bson.objectid import ObjectId
import datetime


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
                product_info_obj = product_info_collection.find_one(query)  # obj type
            except Exception as e:
                print("DB_error : Class Rows.model()", end=" >> ")
                print(e)

            if product_info_obj is not None:
                # print("info_dic : ", end="")
                # print(product_info_dic)
                _week_list.append(product_info_obj['week'])
                _sn_list.append(product_info_obj['sn'])
                _model_id_list.append(product_info_obj['model_id'])
                # _model_list.append(product_info_dic['model'])

        model_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'model')
        for test_item in _model_id_list:
            _object = model_collection.find_one({'_id': ObjectId(test_item)})
            _model_list.append(_object['model'])

        for i in range(0, len(_product_id_list)):
            res = {"product_id": _product_id_list[i], "model": _model_list[i], "sn": _sn_list[i],
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

    def model_list(self):
        print('Load - Class model_list()')
        try:
            # db_object = Mongodb_connection()
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'model')
            rows_list = list(rows_collection.distinct('model'))  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.info()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        # print("all info list")
        for _list in rows_list:
            print(_list)
        return rows_list

    def reason_list(self):
        print('Load - Class model_list()')
        try:
            # db_object = Mongodb_connection()
            rows_collection = self._DB_object.db_conn(self._DB_object.db_client(), 'history')
            rows_list = list(rows_collection.distinct('reason'))  # cursor type -> list type
        except Exception as e:
            print("DB_error : Class Rows.info()", end=" >> ")
            print(e)
        finally:
            self._DB_object.db_close()
        # print("all info list")\
        for _list in rows_list:
            print(_list)
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

