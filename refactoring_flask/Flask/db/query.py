from Flask.py.utils import *
from Flask.db.abstract_query import *


class DatabaseCommand(DatabaseApis):
    @staticmethod
    def get_history_from_show_field(filter_dic):
        query = {"show": '1'}
        cursor = history_coll.find()
        ' 전체 데이터 검색하기 때문에, 대처 방안 마련해야 함 '
        for document in cursor:
            keys = document.keys()
        for key, val in filter_dic.items():
            if key in keys:
                if val and val is not True:
                    query.update({key: {"$regex": val, "$options": 'i'}})
        print('\nQuery : ', end="")
        print(query)
        historyCursor = cursor2jsgrid(history_coll.find(query))
        return historyCursor

    @staticmethod
    def add_info_from_history(history_list, filter_dic):
        def model2id(key, model):
            model = model.split('|')
            _query = list()
            if not model:
                return Response('Invaild Model Input', status=404)
            for slice_model in model:
                result = model_coll.find_one({'model': slice_model})
                if not result:
                    return False
                _query.append({key: result['_id']})
            return _query
        query = {"show": '1'}
        if filter_dic:
            cursor = product_info_coll.find()
            ' 전체 데이터 검색하기 때문에, 대처 방안 마련해야 함 '
            for document in cursor:
                keys = document.keys()
            for key, val in filter_dic.items():
                if key == 'model':
                    key = 'model_id'
                if key in keys:
                    if val and val is not True:
                        if key == 'model_id':
                            val = model2id(key, val)
                            if val:
                                query.update({"$or": val})
                            else:
                                pass
                        else:
                            query.update({key: {"$regex": val, "$options": 'i'}})
            if 'pastDate' and 'nowDate' in filter_dic:
                nowDate = date2week(filter_dic['nowDate'])
                pastDate = date2week(filter_dic['pastDate'])
                date_search_query = {"$and": [{"week": {"$gte": pastDate}}, {"week": {"$lte": nowDate}}]}
                query.update(date_search_query)
            print('query : ', end="")
            print(query)

        if not history_list:
            return Response('\nInvalid history argument\n', status=404)

        length = len(history_list) - 1  # 전체 길이
        while length >= 0:
            query2 = {}
            query2.update(query)
            query2.update({'_id': ObjectId(history_list[length]['product_id'])})
            match_product_info_item = dict2jsgrid(product_info_coll.find_one(query2, {'_id': False}))
            # print(match_product_info_item, end="   --- Added ----> ")
            if not match_product_info_item:
                del history_list[length]
            else:
                history_list[length].update(match_product_info_item)
            length = length - 1

        return history_list

    @staticmethod
    def add_model_from_modelId(product_list):
        if not product_list:
            return product_list
        if type(product_list) != list:
            return Response('\nInvalid list argument\n', status=404)
        for i in range(len(product_list)):
            match_model_item = dict2jsgrid(model_coll.find_one({'_id': ObjectId(product_list[i]['model_id'])}, {'_id': False}))
            # print(match_model_item)
            product_list[i].update(match_model_item)
        return product_list
