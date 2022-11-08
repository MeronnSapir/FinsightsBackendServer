
class CollectionsFormats:

    USERS = {
        'name': '',
        'register_date': '',
        'mail': ''
    }

    HOLDINGS = {
        'ticker': '',
        'market_type': '',
        'shares': '',
        'sector': '',
        'country': '',
        'market_cap': ''
    }

    ORDERS = {
        'user': '',
        'ticker': '',
        'market_type': '',
        'order_type': '',
        'shares': '',
        'date': '',
        'order_price': '',
        'reason': ''
    }


class SSHConfig:
    USERNAME = 'ec2-user'
    PORT = 22


class MongoConfig:
    PRIVATE_KEY = "/Users/meronnsapir/Documents/France2021/AWS-MeronnSapir.pem"
    EC2_URL = '''ec2-18-117-78-221.us-east-2.compute.amazonaws.com'''
    DB_URI = '''ec2-18-117-78-221.us-east-2.compute.amazonaws.com'''
    PORT = 27017


class Queries:
    GET_ORDERS_COLUMNS = {'ticker': 1, 'market_type': 1, 'shares': 1, 'order_price': 1, 'date': 1, 'order_type': 1}

