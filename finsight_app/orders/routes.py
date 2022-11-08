import json
from bson import json_util
from flask import Blueprint, request, make_response
from bson.objectid import ObjectId
from ..db_handler.consts import CollectionsFormats, Queries
from datetime import datetime
from ..config import Collections, TextResponses, StatusCodes, OrderData
from ..db_handler.db_handler import DBHandler


class OrdersBlueprint:

    def __init__(self, db_conn: DBHandler):
        self.db_conn = db_conn
        self.blueprint = self.create_blueprint()
        self.create_get()
        self.create_report_orders()
        self.create_get_orders()
        self.create_delete_orders()

    @staticmethod
    def create_blueprint():
        blueprint = Blueprint('orders', __name__, url_prefix='/orders')
        return blueprint

    def create_get(self):
        @self.blueprint.route('/a')
        def a():
            return '1'

    def create_delete_orders(self):
        @self.blueprint.route('/delete_orders', methods=['GET', 'POST', 'OPTIONS'])
        def delete_orders():
            try:
                request_data = request.get_json()
                user = request_data['user']
                orders_to_remove = request_data['orders']
                print('All orders:')
                print(orders_to_remove)
                undeleted_orders_tickers = self.get_undeleted_orders(orders_to_remove)
                print('Undeleted orders tickers:')
                print(undeleted_orders_tickers)
                orders_to_remove = [order for order in orders_to_remove if
                                    order['ticker'] not in undeleted_orders_tickers]
                ids_to_remove = [ObjectId(order['_id']) for order in orders_to_remove]
                print('Updated orders to remove:')
                print(orders_to_remove)
                res = self.db_conn.mongo_client.get_collection('Orders').delete_many({'_id': {'$in': ids_to_remove}})
                print(res.acknowledged)
                print(res.deleted_count)
                for order in orders_to_remove:
                    self.update_portfolio(shoule_add=False, user=user, ticker=order['ticker'],
                                          quantity=float(order['shares']), order_type=order['order_type'],
                                          market_type=order['market_type'])
                if res.deleted_count:
                    if undeleted_orders_tickers:
                        return TextResponses.PARTLY_DELETED_ORDERS + str(undeleted_orders_tickers), StatusCodes.OK
                    else:
                        return TextResponses.ACKNOWLEDGED, StatusCodes.OK
                if not res.deleted_count:
                    if undeleted_orders_tickers:
                        return TextResponses.UNDELETED_ORDERS_HOLDING_IN_MINUS, StatusCodes.OK
                    return TextResponses.NOT_ACKNOWLEDGED
                return TextResponses.FAILED_TO_UPDATE, StatusCodes.INTERNAL_ERROR
            except Exception as e:
                print(e)
                return TextResponses.FAILED_TO_UPDATE, StatusCodes.INTERNAL_ERROR

    def create_get_orders(self):
        @self.blueprint.route('/get_orders', methods=['GET', 'POST', 'OPTIONS'])
        def get_orders():
            # time.sleep(2)
            key = 0
            try:
                user = request.get_json()['user']
                response = self.db_conn.mongo_client.get_collection('Orders').find({'user': user},
                                                                                   Queries.GET_ORDERS_COLUMNS)
                orders = json.loads(json_util.dumps(response))
                for order in orders:
                    order['_id'] = order['_id']['$oid']
                    order['key'] = key
                    key += 1
                print(orders)
                return orders
            except Exception as e:
                print(e.__str__())

    def create_report_orders(self):
        @self.blueprint.route('/report_order', methods=['POST', 'OPTIONS'])
        def report_order():
            try:
                request_data = request.get_json()
                print(request_data)
                if self.validate_order_data(request_data):
                    request_data['insertion_time'] = datetime.now()
                    res = self.db_conn.insert_to_collection(collection=Collections.ORDERS, document=request_data)
                    if res == TextResponses.ACKNOWLEDGED:
                        update_res = self.update_portfolio(shoule_add=True,
                                                           user=request_data['user'],
                                                           market_type=request_data['market_type'],
                                                           ticker=request_data['ticker'],
                                                           order_type=request_data['order_type'],
                                                           quantity=float(request_data['shares']))
                        if update_res != TextResponses.ACKNOWLEDGED:
                            print(update_res.title() + ' unacknowledged')
                        return TextResponses.ACKNOWLEDGED, StatusCodes.OK
                    if res == TextResponses.NOT_ACKNOWLEDGED:
                        return TextResponses.NOT_ACKNOWLEDGED
                    if res == TextResponses.DOCUMENT_ALREADY_EXISTS:
                        return TextResponses.DOCUMENT_ALREADY_EXISTS
                    return TextResponses.FAILED_TO_UPDATE, StatusCodes.INTERNAL_ERROR
                return TextResponses.UNVALID_DOCUMENT, StatusCodes.BAD_REQUEST
            except Exception as e:
                print(e.__str__())

    def update_portfolio(self, shoule_add: bool, user: str, ticker: str, order_type: str, quantity: float,
                         market_type: str):
        print(user)
        print(ticker)
        current_holding = self.db_conn.mongo_client.get_collection('Holdings').find_one({
            'user': user,
            'ticker': ticker})
        print('The current holding is:')
        print(current_holding)
        if current_holding:
            if order_type == 'sell' and quantity > float(current_holding['quantity']):
                return TextResponses.SELL_QTY_TOO_HIGH
            change = quantity if (order_type == 'buy') == shoule_add else -quantity
            res = self.db_conn.mongo_client.get_collection('Holdings').update_one({'ticker': ticker},
                                                                                  {'$inc': {'quantity': float(change)}})
            print('sell order of ' + ticker + ':')
            print(res.acknowledged)
            self.db_conn.mongo_client.get_collection('Holdings').update_one({'ticker': ticker},
                                                                            {'$set': {'last_updated': datetime.now()}})
            return TextResponses.ACKNOWLEDGED if res.acknowledged else TextResponses.NOT_ACKNOWLEDGED
        if order_type == 'buy':
            print('Hey')
            res = self.db_conn.insert_to_collection(collection=Collections.HOLDINGS, document={
                'user': user,
                'ticker': ticker,
                'market_type': market_type,
                'quantity': float(quantity),
                'first_updated': datetime.now(),
                'last_updated': datetime.now()
            })
            print('Buy order of ' + ticker + ':')
            print(res)
            return res
        print(ticker + " sell order's quantity was too high and over the holding")
        return TextResponses.SELL_QTY_TOO_HIGH

    def get_undeleted_orders(self, orders_to_remove: list):
        undeleted_orders = []
        for order in orders_to_remove:
            print('order:')
            print(order)
            if order['order_type'] == 'buy':
                holding_quantity = \
                    float(self.db_conn.mongo_client.get_collection(Collections.HOLDINGS).find_one({'ticker': order['ticker']},
                                                                                            {'quantity': 1})['quantity'])
                print(holding_quantity)
                if float(order['shares']) > holding_quantity:
                    undeleted_orders.append(order['ticker'])
        return undeleted_orders

    @staticmethod
    def validate_order_data(order_data: dict):
        expected_keys = set(CollectionsFormats.ORDERS.keys())
        print(expected_keys)
        request_keys = set(order_data)
        print('requested keys - ', str(request_keys))
        return request_keys.issubset(expected_keys)
