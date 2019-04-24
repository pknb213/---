from pymongo import MongoClient


class MongodbConnection:
    def __init__(self):
        # print(" ~~ ", sep = '\n')
        print("MongoDB init")
        self._ip = '222.106.48.150'
        self._port = 27019

    def db_client(self):
        return MongoClient(self._ip, self._port)

    def db_conn(self, client, coll):
        try:
            if not 'ERP_refacDB' in client.list_database_names():
                client['ERP_refacDB'].create_collection('model')
                client['ERP_refacDB'].create_collection('history')
                client['ERP_refacDB'].create_collection('product_info')
                client['ERP_refacDB'].create_collection('manufacture')
            db = client['ERP_refacDB']
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


mongoClient = MongoClient('222.106.48.150', 27019)
if not 'ERP_refacDB' in mongoClient.list_database_names():
    mongoClient['ERP_refacDB'].create_collection('model')
    mongoClient['ERP_refacDB'].create_collection('history')
    mongoClient['ERP_refacDB'].create_collection('product_info')
    mongoClient['ERP_refacDB'].create_collection('manufacture')

model_coll = mongoClient['ERP_refacDB']['model']
history_coll = mongoClient['ERP_refacDB']['history']
product_info_coll = mongoClient['ERP_refacDB']['product_info']
manufacture_coll = mongoClient['ERP_refacDB']['manufacture']
users_coll = mongoClient['ERP_refacDB']['users']


