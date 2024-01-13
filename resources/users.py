from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity

from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

bp = Blueprint("users", __name__, description="Operations on users")

@bp.route("/refresh")
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti) #use refresh token only once
        return {"access_token": access_token}

@bp.route("/register")
class UserRegister(MethodView):
    @bp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(400, message="User already exists")
        user = UserModel(username=user_data["username"], password=sha256.hash(user_data["password"]))
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully"}

@bp.route("/user/<int:user_id>")
class UserById(MethodView):
    @bp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}
    
@bp.route("/login")
class UserLogin(MethodView):
    @bp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()
        if not user or not sha256.verify(user_data["password"], user.password):
            abort(401, message="Invalid username or password")
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}    
    
@bp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}