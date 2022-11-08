from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
from .consts import SSHConfig, MongoConfig
from ..config import TextResponses


class DBHandler:

    def __init__(self):
        self.ssh_tunnel = self.create_ssh_tunnel()
        self.mongo_client = self.crate_mongo_conn()

    @staticmethod
    def create_ssh_tunnel():
        tunnel = SSHTunnelForwarder(
            (MongoConfig.EC2_URL, SSHConfig.PORT),
            ssh_username=SSHConfig.USERNAME,                # I used an Ubuntu VM, it will be ec2-user for you
            ssh_pkey=MongoConfig.PRIVATE_KEY,   # I had to give the full path of the keyfile here
            remote_bind_address=(MongoConfig.DB_URI, MongoConfig.PORT),
            local_bind_address=('0.0.0.0', MongoConfig.PORT)
        )
        print(tunnel)
        tunnel.start()
        return tunnel

    def close_ssh_tunnel(self):
        self.ssh_tunnel.stop()

    @staticmethod
    def crate_mongo_conn():
        mongo_client = MongoClient(
            host='127.0.0.1',
            port=MongoConfig.PORT
        )
        db = mongo_client['Finsights']
        return db

    def insert_to_collection(self, collection: str, document: dict):
        # try:
            collection = self.mongo_client[collection]
            if collection.name == 'Orders' and self.is_document_exists(collection=collection.name, document=document):
                print(TextResponses.DOCUMENT_ALREADY_EXISTS)
                return TextResponses.DOCUMENT_ALREADY_EXISTS
            res = collection.insert_one(document=document).acknowledged
            if not res:
                print('PALIIII')
                # print(res)
                return TextResponses.NOT_ACKNOWLEDGED
            return TextResponses.ACKNOWLEDGED
        # except Exception as e:
        #     print(e.__str__())
        #     return TextResponses.FAILED_TO_UPDATE

    def is_document_exists(self, collection: str, document: dict):
        document.pop('insertion_time')
        document.pop('reason')
        return bool(self.mongo_client[collection].find(document).count())



