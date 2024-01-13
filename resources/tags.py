from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError



from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

bp = Blueprint("tags", __name__, description="Operations on tags")

@bp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @bp.arguments(TagSchema)
    @bp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        # if TagModel.query.filter_by(name=tag_data["name"], store_id=store_id).first():
        #     abort(400, message="Tag already exists") // it will alwys fail as tag unique constraint is true
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        
        except IntegrityError:
            abort(400, message="Tag already exists")
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag      

@bp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @bp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if item.store_id != tag.store_id:
            abort(400, message="Item and tag must belong to the same store")
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))    

        return tag
    
    @bp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag not in item.tags:
            abort(400, message="Tag not linked to item")
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))    

        return {"message": "Tag removed from item", "item": item, "tag": tag}

@bp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @bp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @bp.response(202, description="Deletes a tag if no item is linked to it", examples={"message": "Tag deleted"})
    @bp.alt_response(404, description="Tag not found")
    @bp.alt_response(400, description="Tag is linked to an item")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(400, message="Tag is linked to an item")