from Flask.py.utils import *
from Flask.db.pymongodb import *
from Flask.db.query import DatabaseCommand


class Product:
    def __init__(self):
        print("Product class")

    'key를 추가하고 value를 공백으로 설정'
    @staticmethod
    def validate_request(req, *keys):
        for k in keys:
            if k not in req: req[k] = ''

    @staticmethod
    def get_model(req):
        if not req:
            return Response('\nInvalid argument\n', status=404)
        for i in range(len(req)):
            req[i]['_id'] = str(req[i]['_id'])

        print('\n>>>>>>>>>\n')
        for item in req:
            print(item)
        return req

    @staticmethod
    def show_model():
        modelCursor = cursor2jsgrid(model_coll.find())
        for i in modelCursor:
            print(i)
        return jsonify(modelCursor)

    @staticmethod
    def show_product_info():
        productInfoCursor = cursor2jsgrid(product_info_coll.find())
        for i in productInfoCursor:
            print(i)
        return jsonify(productInfoCursor)

    @staticmethod
    def show_history():
        historyCursor = cursor2jsgrid(history_coll.find())
        for i in historyCursor:
            print(i)
        return jsonify(historyCursor)

    @staticmethod
    def show_main_table_rows(filter_dic):
        print("Execution : show_main_table_rows()", end=" ")
        # test()
        print(utc.localize(datetime.datetime.utcnow()).astimezone(KST).strftime(fmt))
        print("Filter Dic : ", end="")
        print(filter_dic)
        rows = DatabaseCommand.get_history_from_show_field(filter_dic)
        rows = DatabaseCommand.add_info_from_history(rows, filter_dic)
        rows = DatabaseCommand.add_model_from_modelId(rows)
        # print("\nResult ---------------------------------")
        # for i in rows:
        #     print(i)
        if type(rows) is not list:
            return Response(status=200)
        return jsonify(rows)

    @staticmethod
    def add_table_row(req):  # model, sn, week, location, state, reason, btn
        print("Execution : add_table_row()")
        model_name_db_list = Product.model_db_list()
        if req['model'] not in model_name_db_list:
            return Response('\nInvalid name\n', status=404)
        if not req['sn']:
            return Response('\nInvalid sn\n', status=404)
        if not req['week']:
            return Response('\nInvalid week\n', status=404)
        if not req['location']:
            return Response('\nInvalid location\n', status=404)
        if not req['state']:
            return Response('\nInvalid state\n', status=404)

        model_dic = model_coll.find_one({'model': req['model']}, {'model': False})
        resultOfProductInsertOne = product_info_coll.insert_one({'model_id': model_dic['_id'], 'sn': req['sn'],
                                                                 'week': req['week'], 'show': '1', 'quality': 'N'})

        history_coll.insert_one({'product_id': resultOfProductInsertOne.inserted_id, 'show': '1', 'date': utc.localize(datetime.datetime.utcnow()).astimezone(KST).strftime(fmt),
                                 'location': req['location'], 'state': req['state'], 'reason': req['reason']})

        return Response(status=200)

    @staticmethod
    def update_table_row(req):     # row information about id, date, header, location, model, state, reason, quality etc
        print("Execution : update_table_row()")
        model_name_db_list = Product.model_db_list()
        if req['model'] not in model_name_db_list:
            return Response('\nInvalid name\n', status=404)
        if not req['sn']:
            return Response('\nInvalid sn\n', status=404)
        if not req['week']:
            return Response('\nInvalid week\n', status=404)
        if not req['location']:
            return Response('\nInvalid location\n', status=404)
        if not req['state']:
            return Response('\nInvalid state\n', status=404)

        model_dic = model_coll.find_one({'model': req['model']}, {'model': False})
        # print(model_dic)

        history_coll.update_one({'_id': ObjectId(req['_id'])}, {'$set': {'location': req['location'],
                                                                         'state': req['state'], 'reason': req['reason']}})
        product_info_coll.update_one({'_id': ObjectId(req['product_id'])}, {'$set': {'model_id': ObjectId(model_dic['_id']),
                                                                                     'sn': req['sn'], 'week': req['week']}})
        return Response(status=200)

    @staticmethod
    def model_db_list():
        return model_coll.distinct('model')

    @staticmethod
    def delete_table_row(req):     # row information about id, date, header, location, model, state, reason, quality etc
        print("Execution : delete_table_row()")
        if not req:
            return Response('\nInvalid Request form\n', status=404)

        product_info_coll.delete_one({'_id': req['product_id']})

        '''------------------------------------------------------------------
        < Anything failed to delete > 
        result : <pymongo.results.DeleteResult object at 0x00000242BDF50208>
        result.acknowledged : True
        result.deleted_count : 0
        result.raw_result : {'n': 0, 'ok': 1.0}
        
        < Delete success >
        result : <pymongo.results.DeleteResult object at 0x0000021B683F9B08>
        result.acknowledged : True
        result.deleted_count : 1
        result.raw_result : {'n': 1, 'ok': 1.0}
        -------------------------------------------------------------------'''
        result = history_coll.delete_one({'_id': ObjectId(req['_id'])})
        if result.deleted_count != 1:
            return Response('\nInvalid history Id\n', status=404)
        find_list = cursor2jsgrid(history_coll.find({'product_id': ObjectId(req['product_id'])}))
        if not find_list:
            return Response(status=200)

        ' before Bubble sorting '
        for item in find_list:
            print(item)

        ' Bubble Sorting '
        for i in range(len(find_list)-1):
            for j in range(len(find_list)-i-1):
                if find_list[j]['show'] == '1':
                    return Response('\nInvalid show parameter\n', status=404)
                if find_list[j]['date'] < find_list[j+1]['date']:
                    find_list[j], find_list[j+1] = find_list[j+1], find_list[j]

        ' After Bubble sorting '
        print('\n')
        for item in find_list:
            print(item)

        '''---------------------------------------------------------------
        < Update success >
        result : <pymongo.results.UpdateResult object at memory address>
        result.acknowledged : True
        result.upserted_id : None
        result.raw_result : {'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}
        result.matched_count : 1
        result.modified_count : 1
        ---------------------------------------------------------------'''
        recently_history_id = find_list[0]['_id']
        result = history_coll.update_one({'_id': ObjectId(recently_history_id)}, {'$set': {'show': '1'}})
        if result.modified_count <= 0:
            return Response('\nFail, Changed recently show value\n', status=404)
        return Response(status=200)

    @staticmethod
    def show_detail_modal_table_rows(product_id):
        print("Execution : show_detail_modal_table_rows()")
        if not product_id:
            return Response(status=200)
        print(utc.localize(datetime.datetime.utcnow()).astimezone(KST).strftime(fmt))
        rows = Product.get_history_from_productId(product_id)
        rows = DatabaseCommand.add_info_from_history(rows, None)
        rows = DatabaseCommand.add_model_from_modelId(rows)
        print("\nResult -----------------------------")
        for i in rows:
            print(i)
        return jsonify(rows)

    @staticmethod
    def get_history_from_productId(product_id):
        historyCursor = cursor2jsgrid(history_coll.find({'product_id': ObjectId(product_id)}))
        print(historyCursor)
        return historyCursor

    @staticmethod
    def add_detail_table(req, product_id):
        print("Execution : add_detail_table()")
        if not product_id:
            return Response('\nInvalid product_id\n', status=404)
        if not req['date']:
            return Response('\nInvalid name\n', status=404)

        recently_history = history_coll.find_one({'product_id': ObjectId(product_id), 'show': '1'}, {'product_id': False, 'location': False,
                                                                                                         'state': False, 'reason': False,
                                                                                                         'note': False})
        if not recently_history:
            return Response("\nCan't find the recently_history", status=404)

        if recently_history['date'] > req['date']:
            show = '0'
        elif recently_history['date'] == req['date']:
            return Response("\n Don't inserted same date\n", status=404)
        else:
            show = '1'
            result = history_coll.update_one({'_id': ObjectId(product_id)}, {'$set': {'show': '0'}})
            if result.modified_count <= 0:
                return Response('\nFail, Changed recently show value\n', status=404)

        history_coll.insert_one({'product_id': ObjectId(product_id), 'date': req['date'], 'location': req['location'],
                                 'show': show, 'state': req['state'], 'reason': req['reason'], 'note': req['note']})
        return Response(status=200)

    @staticmethod
    def update_detail_table(req, product_id):
        print("Execution : update_detail_table()")
        if not product_id:
            return Response('\nInvalid product_id\n', status=404)
        if not req:
            return Response('\nInvalid request form\n', status=404)

        result = history_coll.update_one({'_id': ObjectId(req['_id'])}, {'$set': {'date': req['date'],
                                                                                  'location': req['location'],
                                                                                  'state': req['state'],
                                                                                  'reason': req['reason'],
                                                                                  'note': req['note']}})
        if result.modified_count <= 0:
            return Response('\nFailed update_one function\n', status=404)
        return Response(status=200)

    @staticmethod
    def delete_detail_table(req, product_id):
        print("Execution : delete_detail_table()")
        if not product_id:
            return Response('\nInvalid product_id\n', status=404)
        if not req:
            return Response('\nInvalid request form\n', status=404)

        history = history_coll.find_one({'_id': ObjectId(req['_id'])})
        show_value = history['show']

        if not show_value:
            return Response("\nHistory have not show value\n", status=404)
        elif show_value == '0':
            result = history_coll.delete_one({'_id': ObjectId(req['_id'])})
            if result.deleted_count != 1:
                return Response('\nInvalid history Id\n', status=404)
            return Response(status=200)

        result = history_coll.delete_one({'_id': ObjectId(req['_id'])})
        if result.deleted_count != 1:
            return Response('\nInvalid history Id\n', status=404)

        find_list = cursor2jsgrid(history_coll.find({'product_id': ObjectId(req['product_id'])}))
        if not find_list:
            return Response(status=200)

        ' before Bubble sorting '
        for item in find_list:
            print(item)

        ' Bubble Sorting '
        for i in range(len(find_list) - 1):
            for j in range(len(find_list) - i - 1):
                if find_list[j]['show'] == '1':
                    return Response('\nInvalid show parameter\n', status=404)
                if find_list[j]['date'] < find_list[j + 1]['date']:
                    find_list[j], find_list[j + 1] = find_list[j + 1], find_list[j]

        ' After Bubble sorting '
        print('\n')
        for item in find_list:
            print(item)

        recently_history_id = find_list[0]['_id']
        result = history_coll.update_one({'_id': ObjectId(recently_history_id)}, {'$set': {'show': '1'}})
        if result.modified_count <= 0:
            return Response('\nFail, Changed recently show value\n', status=404)

        return Response(status=200)
