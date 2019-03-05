import pymongo


class MongodbConnection:
    def __init__(self):
        # print(" ~~ ", sep = '\n')
        print("MongoDB init")
        self._ip = '222.106.48.150'
        self._port = 27019

    def db_client(self):
        return pymongo.MongoClient(self._ip, self._port)

    def db_conn(self, client, coll):
        try:
            db = client['ERP_test']
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
