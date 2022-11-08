
class APIConfig:
    DB_CONN = 'db_conn'


class Collections:
    USERS = 'Users'
    ORDERS = 'Orders'
    HOLDINGS = 'Holdings'


class TextResponses:
    SUCCESS = 'Success'
    ACKNOWLEDGED = 'Acknowledged'
    NOT_ACKNOWLEDGED = 'Not acknowledged'
    DOCUMENT_ALREADY_EXISTS = 'Document already exists'
    FAILED_TO_UPDATE = 'Failed to update'
    UNVALID_DOCUMENT = 'Document is unvalid'
    SELL_QTY_TOO_HIGH = 'The sell quantity is over your current holding'
    PARTLY_DELETED_ORDERS = 'Acknowledged, but some orders were not deleted. Pay attention not to leave more selled shares than bought ones in ticker: '
    UNDELETED_ORDERS_HOLDING_IN_MINUS = 'We could not delete the orders since they left the holdings in your account to a negative number. Try deleting buy orders first'


class OrderData:
    KEY_LIST = ['ticker', 'order_type', 'shares', 'order_price', 'reason', 'date', 'market_type', 'user']


class StatusCodes:
    OK = 200
    BAD_REQUEST = 400
    INTERNAL_ERROR = 500


class Polygon:
    API_KEY = "6PatT69p_OLAdR19ZDzn8N5CnHiJZ4Yh"
    POLYGON_SERVER = "https://api.polygon.io/v2"


