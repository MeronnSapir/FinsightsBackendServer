from flask import Flask, request, make_response
from .db_handler.db_handler import DBHandler
from flask_cors import CORS
from .config import APIConfig
from .data.routes import DataBlueprint
from .orders.routes import OrdersBlueprint


app = Flask(__name__)
cors = CORS(app)
db_conn = DBHandler()
orders_blueprint = OrdersBlueprint(db_conn=db_conn)
data_blueprint = DataBlueprint(db_conn=db_conn)
app.register_blueprint(orders_blueprint.blueprint)
app.register_blueprint(data_blueprint.blueprint)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

@app.before_request
def _build_cors_preflight_response():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response


if __name__ == "__main__":
    app.run(debug=True)
