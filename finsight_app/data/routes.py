from flask import Blueprint, current_app, request
from ..db_handler.db_handler import DBHandler
from ..config import Collections
from ..yahoo_finance.yahoo_finance_api import YahooFinanceAPI


class DataBlueprint:

    def __init__(self, db_conn: DBHandler):
        self.db_conn = db_conn
        self.blueprint = self.create_blueprint()
        self.create_get_balances()
        self.create_get_portfolio_segmentation()
        self.create_get_market_segmentation()
        self.create_get_top_movers()

    @staticmethod
    def create_blueprint():
        blueprint = Blueprint('data', __name__, url_prefix='/data')
        return blueprint

    def create_get_balances(self):
        @self.blueprint.route('/get_balance', methods=['OPTIONS', 'GET'])
        def get_balance():
            balance = 0
            args = request.args
            user = args['user']
            response_list = list(self.db_conn.mongo_client.get_collection(Collections.HOLDINGS).find({'user': user}))
            print(response_list)
            for document in response_list:
                ticker = document['ticker']
                shares = document['quantity']
                balance += YahooFinanceAPI.get_current_price(ticker=ticker) * shares
                print(ticker)
                print(shares)
                print(balance)
            return str(int(balance))

    def create_get_balance_history(self):
        @self.blueprint.route('/get_balance_history', methods=['OPTIONS', 'GET'])
        def get_balance_history():
            return 1

    def create_get_portfolio_segmentation(self):
        @self.blueprint.route('/get_portfolio_segmentation', methods=['OPTIONS', 'GET'])
        def get_portfolio_segmentation():
            args = request.args
            user = args['user']
            data = []
            holdings = list(self.db_conn.mongo_client.get_collection(Collections.HOLDINGS).find({'user': user}))
            total_balance = 0
            for holding in holdings:
                print(holding)
                holding_balance = YahooFinanceAPI.get_current_price(ticker=holding['ticker']) * \
                                holding['quantity']
                holding['holding_balance'] = holding_balance
                total_balance += holding_balance
                print(total_balance)
            for holding in holdings:
                row = {
                    'ticker': holding['ticker'],
                    'holding_balance': holding['holding_balance'],
                    'y': round(holding['holding_balance'] / total_balance * 100)
                }
                data.append(row)
                print(row)
            return data

    def create_get_market_segmentation(self):
        @self.blueprint.route('/get_market_segmentation', methods=['OPTIONS', 'GET'])
        def get_market_segmentation():
            args = request.args
            user = args['user']
            holdings = list(self.db_conn.mongo_client.get_collection(Collections.HOLDINGS).find({'user': user}))
            stock_value = sum(holding['quantity'] for holding in holdings if holding['market_type'] == 'stock_market')
            crypto_value = sum(holding['quantity'] for holding in holdings if holding['market_type'] == 'crypto')
            return [
                {'market_type': 'Stocks', 'y': round(stock_value / (stock_value + crypto_value)) * 100},
                {'market_type': 'Crypto', 'y': round(crypto_value / (stock_value + crypto_value)) * 100},
            ]

    def create_get_top_movers(self):
        @self.blueprint.route('/get_top_movers', methods=['OPTIONS', 'GET'])
        def get_top_movers():
            movers = []
            args = request.args
            user = args['user']
            time_back = args['time_back']
            holdings = list(self.db_conn.mongo_client.get_collection(Collections.HOLDINGS).find({'user': user}))
            for holding in holdings:
                current_price = YahooFinanceAPI.get_current_price(ticker=holding['ticker'])
                print(current_price)
                historic_price = YahooFinanceAPI.get_historic_price(ticker=holding['ticker'], time_back=time_back)
                print(historic_price)
                data = {
                    'ticker': holding['ticker'],
                    'current_price': current_price,
                    'move': float((current_price / historic_price - 1) * 100)
                }
                movers.append(data)
            print(movers)
            sorted_movers = sorted(movers, key=lambda d: -abs(d['move']))
            return sorted_movers

    def document_balance_history(self, user: str, interval: int):
        first_day = "Get the first trade date"
        trades = [{"Get user's trades sorted by dates": 'a'}]
        holdings = {"Get the holdings": 'b'}
        dates_list = ['Create a list of dates based the first date, the interval, and the last day']
        for trade in trades:
            ticker_already_exists = (trade['ticker'] in holdings.keys())
            if trade['order_type'] == 'buy':
                if ticker_already_exists:
                    "Add it to existing holding"
                else:
                    "create new holding"
            elif trade['order_type'] == 'sell':
                if ticker_already_exists:
                    "Reduce it from existing holding"
