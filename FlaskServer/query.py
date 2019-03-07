# 재고 관리
from bson import ObjectId
import datetime

''''#####################################################

Query return value
    find function : Cursor Type
    insert function : Object Type
    update function : Dict Type
    
#####################################################'''


def insert_model(collection, model):
    # Add Meta Data Later.
    query = {'model': model}
    return collection.insert(query)  # Return value is ObjectId


def insert_history(collection, args_list):
    query = {'product_id': args_list[0],
             'show': '1',
             'date': args_list[1],
             'location': args_list[2],
             'state': args_list[3],
             'reason': args_list[4]}
    return collection.insert(query)


def find_production_info_item(coll, product_id):
    query = {
        u"_id": ObjectId(product_id)
    }
    return coll.find(query)


def insert_product_info(collection, args_list):
    query = {'model_id': args_list[0], 'model': args_list[1], 'sn': args_list[2], 'header': args_list[3],
             'week': args_list[4], 'quality': args_list[5], 'show': args_list[6]}

    return collection.insert(query)  # Return value is ObjectId


def find_history_all_item(coll, product_id):
    query = {
        u"product_id": {
            u"$eq": product_id
        }
    }
    return coll.find(query)


def find_history_item(coll, product_id):
    query = {
        "$and":
            [
                {
                    u"product_id": {
                        u"$eq": product_id
                    }
                },
                {
                    'show': {'$eq': '1'}
                }
            ]
    }
    return coll.find(query)


def update_history(collection, product_id):
    match_query = {'product_id': product_id}
    value_query = {'$set': {'show': '0'}}
    return collection.update(match_query, value_query, multi=True)


# 생산 관리
def find_number_of_model(coll, arg, arg2):
    query = {
        u"model": {
            u"$eq": arg
        },
        u"week": {
            u"$eq": arg2
        }
    }
    return coll.find(query).count()


def search_week(coll, data_list):
    query = {}
    return coll.find(query)


def insert_manufacture_info(collection, data_list):
    # Add Meta Data Later.
    query = {'week': data_list[0], 'model': data_list[1], 'number': data_list[2], 'date': data_list[3]}
    return collection.insert(query)  # Return value is ObjectId


# 영업
def insert_partner_list(collection, data_list):
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    query = {'classification': data_list[0], 'partner_name_field': data_list[1], 'b_field': data_list[2],
             'address_field': data_list[3],
             'header_field': data_list[4], 'phone_field': data_list[5], 'email_field': data_list[6],
             'var_field': data_list[7],
             'date': date}
    return collection.insert(query)



# 통계