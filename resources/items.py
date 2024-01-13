# import uuid
# from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
# from db import items, stores
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema, TagAndItemSchema
bp = Blueprint("items", __name__, description="Operations on items")


@bp.route("/item")
class Item(MethodView):
    @jwt_required()
    @bp.response(200, ItemSchema(many=True))
    def get(self):
        # return items.values()
        return ItemModel.query.all()
    
    @jwt_required(fresh=True)
    @bp.arguments(ItemSchema)
    @bp.response(201, ItemSchema)
    def post(self, item_data):
        # item_data = request.get_json()
        # if ("price" not in item_data or "store_id" not in item_data or "name" not in item_data):
        #     abort(400, message="Bad Request. Ensure 'price', 'store_id' and 'name' are included in JSON payload")

        # for item in items.values():
        #     if item["name"] == item_data["name"] and item["store_id"] == item_data["store_id"]:
        #         abort(400, message="Item already exists")

        # if item_data["store_id"] not in stores:
        #     abort(400, message="Store not found")

        # item_id= uuid.uuid4().hex
        # item = {**item_data, "id": item_id}
        # items[item_id] = item
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")
        return item

@bp.route("/item/<int:item_id>")
class ItembyId(MethodView):
    @jwt_required()
    @bp.response(200, ItemSchema)
    def get(self, item_id):
        # try:
        #     return items[item_id]
        # except KeyError:
        #     abort(404, message="Item not found")
        item = ItemModel.query.get_or_404(item_id)
        return item
    
    @jwt_required()
    def delete(self, item_id):
        # try:
        #     del items[item_id]
        #     return {"message": "Item deleted"}
        # except KeyError:
        #     abort(404, message="Item not found")
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted"}
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the item")
    
    @jwt_required()
    @bp.arguments(ItemUpdateSchema)
    @bp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        # item_data = request.get_json()
        # if ("price" not in item_data or "name" not in item_data):
        #     abort(400, message="Bad Request. Ensure 'price' and 'name' are included in JSON payload")
        # try:
        #     item = items[item_id]
        #     item |= item_data
        #     return item
        # except KeyError:
        #     abort(404, message="Item not found")
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id,**item_data)

        db.session.add(item)
        db.session.commit()
        return item    
