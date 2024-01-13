# import uuid
# from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
# from db import stores
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import StoreModel
from schemas import StoreSchema
bp = Blueprint("stores", __name__, description="Operations on stores")

@bp.route("/store")
class Store(MethodView):
    @bp.response(200, StoreSchema(many=True))
    def get(self):
        # return stores.values()
        
        return StoreModel.query.all()
    
    @bp.arguments(StoreSchema)
    @bp.response(201, StoreSchema)
    def post(self, store_data):
        # store_data = request.get_json()
        # if "name" not in store_data:
        #     abort(400, message="Bad Request. Ensure 'name' is included in JSON payload")
        # for store in stores.values():
        #     if store["name"] == store_data["name"]:
        #         abort(400, message="Store already exists")    
        # store_id= uuid.uuid4().hex
        # store = {**store_data, "id": store_id}
        # stores[store_id] = store
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Store already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the store")

        return store
    
@bp.route("/store/<int:store_id>")
class StorebyId(MethodView):
    @bp.response(200, StoreSchema)
    def get(self, store_id):
        # try:
        #     return stores[store_id]
        # except KeyError:
        #     abort(404, message="Store not found")
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    def delete(self, store_id):
        # try:
        #     del stores[store_id]
        #     return {"message": "Store deleted"}
        # except KeyError:
        #     abort(404, message="Store not found")
        store = StoreModel.query.get_or_404(store_id)
        try:
            db.session.delete(store)
            db.session.commit()
            return {"message": "Store deleted"}
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the store")