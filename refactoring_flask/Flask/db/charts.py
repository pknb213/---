from Flask.py.utils import *
from Flask.db.pymongodb import *
from collections import Counter
from Flask.db.query import DatabaseCommand


class Chart(DatabaseCommand):
    def __init__(self):
        print("Chart class")

    @staticmethod
    def show_chart_table_two(post, *flag):
        columnField = False
        for key, val in post.items():
            print("key : %s    val : %s" % (key, val))
            if val is True:
                columnField = key

        def pipeline(model_id, reason):
            _pipeline = [
                {
                    "$lookup":
                        {
                            "from": "history",
                            "localField": "_id",
                            "foreignField": "product_id",
                            "as": "history_coll"
                        }

                },
                {
                    "$unwind": "$history_coll"
                },
                {
                    "$match":
                        {
                            'history_coll.show': '1', 'history_coll.state': reason, 'model_id': model_id
                        }
                },
                {
                    "$project":
                        {
                            "history_coll.state": 1, "model_id": 1
                        }
                }
            ]
            return _pipeline

        rows = []
        model_result = list(model_coll.find())
        for model in model_result:
            row = {}
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "재고")))
            row.update({"모델": model['model'], "재고": len(result)})
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "출고")))
            row.update({"출고": len(result)})
            rows.append(row)
        print("<<<<< Test >>>>>")
        for i in rows:
            print(i)

        return jsonify(rows)

    @staticmethod
    def show_chart_table4(post):
        query = {"show": '1'}
        _pipeline = []
        _match_query = {}
        _project_query = {}
        _show_query = {}

        product_keys = getKeys("product_info")
        history_keys = getKeys("history")
        model_keys = getKeys("model")

        as_history = "history_coll"
        as_model = "model_coll"

        for key, val in post.items():
            _lookup_query = {}
            _unwind_query = {}
            if key in product_keys:
                query.update({key: {"$regex": val, "$options": 'i'}})
            if key in history_keys:
                query.update({as_history + '.' + str(key): {"$regex": val, "$options": 'i'}})
            _lookup_query = {
                "$lookup":
                    {
                        "from": "history",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": as_history
                    }

            }
            _unwind_query = {
                "$unwind": "$history_coll"
            }
            _match_query = {
                "$match":
                    {
                        "history_coll.show": {"$eq": '1'}
                    }
            }
            _pipeline.append(_lookup_query)
            _pipeline.append(_unwind_query)
            _pipeline.append(_match_query)
            if key in model_keys:
                query.update({as_model + '.' + str(key): {"$regex": val, "$options": 'i'}})
                _lookup_query = {
                    "$lookup":
                        {
                            "from": "model",
                            "localField": "model_id",
                            "foreignField": "_id",
                            "as": as_model
                        }
                }
                _unwind_query = {
                    "$unwind": "$model_coll"
                }
            else:
                _lookup_query = {
                    "$lookup":
                        {
                            "from": "model",
                            "localField": "model_id",
                            "foreignField": "_id",
                            "as": as_model
                        }
                }
                _unwind_query = {
                    "$unwind": "$model_coll"
                }
            if _lookup_query:
                _pipeline.append(_lookup_query)
                _pipeline.append(_unwind_query)

        if 'pastDate' and 'nowDate' in post:
            nowDate = date2week(post['nowDate'])
            pastDate = date2week(post['pastDate'])
            query.update({"$and": [{"week": {"$gte": pastDate}}, {"week": {"$lte": nowDate}}]})

        if _pipeline:
            _match_query = {
                "$match":
                    {
                        "$and": [query]
                    }
            }
            _pipeline.append(_match_query)

            _group_query = {
                "$group":
                    {
                        "_id":
                            {
                                "model": "$model_coll.model",
                                "location": "$history_coll.location"
                            },
                        "count": {"$sum": 1}
                    }
            }
            _pipeline.append(_group_query)
            _group_query2 = {
                "$group":
                    {
                        "_id": "$_id",
                        "count": {"$sum": 1},
                    }
            }
            _result_match = {
                "$match":
                    {
                        "$or":
                            [
                                {"_id.location": "대전본부"},
                                {"_id.location": "경북 포항"},
                                {"_id.location": "서울 압구정"}
                            ]
                    }
            }
            _pipeline.append(_result_match)
            if _show_query:
                _project_query = {
                    "$project": _show_query
                }
                _pipeline.append(_project_query)

            _sort_query = {
                "$sort":
                    {
                        "_id.model": 1
                    }
            }
            _pipeline.append(_sort_query)
            print("PipeLine : ")
            print(_pipeline, end="\n\n")

            result = product_info_coll.aggregate(_pipeline)
            result = cursor2jsgrid(result)

        print("\n<<<<< Aggregate Result >>>>>")
        for i in result:
            print(i)

        """ { model, site1, site2, site3 all } """
        merge_result = []
        for _item in result:
            merge_dic = {}
            for key, val in _item.items():
                if type(val) is dict:
                    merge_dic.update(val)
                else:
                    merge_dic.update({key: val})
            merge_result.append(merge_dic)

        for _item in merge_result:
            _item.update({"model": _item["model"], _item["location"]: _item["count"]})
            _item.pop("location")
            _item.pop("count")

        a = []
        del_item_num = []
        for i in range(len(merge_result)):
            for j in range(i+1, len(merge_result)):
                if merge_result[i]["model"] == merge_result[j]["model"]:
                    merge_result[i].update(merge_result[j])
                    del_item_num.append(i)

        print("\n<<<<<<< ... >>>>>>>")
        for i in merge_result:
            print(i)

        del_item_num = set(del_item_num)
        print(set(del_item_num))
        del_item_num = list(del_item_num)

        for i in range(len(del_item_num)):
            del merge_result[del_item_num[i]]
            if del_item_num[i] != del_item_num[-1]:
                del_item_num[i+1] -= i+1

        print("\n<<<<<<< Merge Result >>>>>>>")
        for i in merge_result:
            print(i)

        return jsonify(merge_result)

    @staticmethod
    def show_chart_table2(post, *flag):
        columnField = False
        for key, val in post.items():
            print("key : %s    val : %s" % (key, val))
            if val is True:
                columnField = key
        rows = Chart.get_function(post)

        return jsonify(rows)

    @staticmethod
    def get_function(filter_dic):
        def pipeline(model_id, location):
            _pipeline = [
                {
                    "$lookup":
                        {
                            "from": "history",
                            "localField": "_id",
                            "foreignField": "product_id",
                            "as": "history_coll"
                        }

                },
                {
                    "$unwind": "$history_coll"
                },
                {
                    "$match":
                        {
                            'history_coll.show': '1', 'history_coll.location': location, 'model_id': model_id
                        }
                },
                {
                    "$project":
                        {
                            "history_coll.location": 1, "model_id": 1
                        }
                }
            ]
            return _pipeline

        rows = []
        model_result = list(model_coll.find())
        for model in model_result:
            row = {}
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "대전본부")))
            row.update({"모델": model['model'], "대전본부": len(result)})
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "서울 압구정")))
            row.update({"서울 압구정": len(result)})
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "경북 포항")))
            row.update({"경북 포항": len(result)})
            rows.append(row)
        print("<<<<< Test >>>>>")
        for i in rows:
            print(i)
        return rows

    @staticmethod
    def show_chart_table3(post, *flag):
        columnField = False
        for key, val in post.items():
            print("key : %s    val : %s" % (key, val))
            if val is True:
                columnField = key

        def pipeline(model_id, reason):
            _pipeline = [
                {
                    "$lookup":
                        {
                            "from": "history",
                            "localField": "_id",
                            "foreignField": "product_id",
                            "as": "history_coll"
                        }

                },
                {
                    "$unwind": "$history_coll"
                },
                {
                    "$match":
                        {
                            'history_coll.show': '1', 'history_coll.reason': reason, 'model_id': model_id
                        }
                },
                {
                    "$project":
                        {
                            "history_coll.location": 1, "model_id": 1
                        }
                }
            ]
            return _pipeline

        rows = []
        model_result = list(model_coll.find())
        for model in model_result:
            row = {}
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "출하가능")))
            row.update({"모델": model['model'], "출하가능": len(result)})
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "납품완료")))
            row.update({"납품완료": len(result)})
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "생산")))
            row.update({"생산": len(result)})
            result = list(product_info_coll.aggregate(pipeline(model['_id'], "검증필요")))
            row.update({"검증필요": len(result)})
            rows.append(row)
        print("<<<<< Test >>>>>")
        for i in rows:
            print(i)

        return jsonify(rows)

    @staticmethod
    def show_chart_table(post, *flag):
        columnField = False

        for key, val in post.items():
            print("key : %s    val : %s" % (key, val))
            if val is True:
                columnField = key

        rows = DatabaseCommand.get_history_from_show_field(post)
        rows = DatabaseCommand.add_info_from_history(rows, post)
        rows = DatabaseCommand.add_model_from_modelId(rows)

        '''
          column0에는 model이 들어가야하고
          column1 부터 3까지 딕셔너리 형태의 값이 들어가야한다
          ex) { column0: Indy7, 'column1' : 1, column2: '2', column3: '3' } 
        '''

        '''
            column0는 model의 나열
            column1 ~ n은 columnField와 model이 일치하는 수량
        '''

        if columnField:
            modelSet = set()
            columnSet = set()
            model_count_dic = {}
            column_count_dic = {}
            for row in rows:
                columnSet.add(row[columnField])
                if model_count_dic:
                    if row['model'] in model_count_dic:
                        'result 딕셔너리에 저장된 model key가 있다'
                        if row[columnField] in model_count_dic[row['model']]:
                            'model key를 갖고 있고 field 또한 갖고 있다'
                            model_count_dic[row['model']][row[columnField]] += 1
                        else:
                            'model key를 갖고있지만 field는 없다. 새로운 field를 추가해야한다.'
                            column_count_dic.update({row[columnField]: 1})
                            # model_count_dic.update({row['model']: column_count_dic})
                            model_count_dic[row['model']].update(column_count_dic)
                    else:
                        'result 딕셔너리에 저장된 model key가 없다'
                        model_count_dic.update({row['model']: {row[columnField]: 1}})
                else:
                    'result 딕셔너리가 비었다.'
                    column_count_dic.update({row[columnField]: 1})
                    model_count_dic.update({row['model']: column_count_dic})

            columnSet = list(columnSet)
            if flag:
                print("Return the column")
                return columnSet

            print("\n\n---------------------------")
            for key, val in model_count_dic.items():
                print(key, end=" : ")
                print(val)

            rows = []
            for model, val in model_count_dic.items():
                row = {}
                row.update({'column0': model})
                for i in range(1, len(columnSet)):
                    embedRow = 'column' + str(i)
                    if columnSet[i - 1] in model_count_dic[model].keys():
                        row.update({embedRow: model_count_dic[model][columnSet[i - 1]]})
                # for key, val in model_count_dic[model].items():
                #     embedRow = 'column' + str(i)
                #     row.update({embedRow: model_count_dic[model][key]})
                #     i += 1
                rows.append(row)
            print("\n")
            for row in rows:
                print(row)

        else:
            model_set = set()
            model_count_dic = {}
            for row in rows:
                if row['model'] in model_set:
                    model_count_dic[row['model']] += 1
                else:
                    model_set.add(row['model'])
                    model_count_dic.update({row['model']: 1})

            model_set = list(model_set)
            model_set.sort()
            # print(model_set)
            print(model_count_dic)

            rows = []
            for model in model_set:
                row = {}
                row.update({'column0': model, 'column1': model_count_dic[model]})
                rows.append(row)
            print("\n")
            for row in rows:
                print(row)

        # row = {}
        # for i in range(len(model_set)):
        #     col_number = 'column' + str(i)
        #     if i == 0:
        #         row.update({col_number: model_set[i]})
        #     else:
        #         row.update({col_number: model_count_dic[model_set[i]]})
        #
        # print(row)

        return jsonify(rows)

    @staticmethod
    def get_field_num(post, flag):
        flag = flag['flag']
        print(flag)
        print(type(flag))
        return jsonify(Chart.show_chart_table(post, flag))

    @staticmethod
    def show_chart_table6(post):

        return jsonify(1)
