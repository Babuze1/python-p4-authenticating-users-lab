#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session, Response  # Import Response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class UserResource(Resource):

    def post(self):
        data = request.get_json()
        username = data.get('username')

        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'message': 'User not found'}), 404

class LogoutResource(Resource):

    def delete(self):
        if 'user_id' in session:
            session.pop('user_id', None)
            return {}, 204
        else:
            return jsonify({'message': 'Not logged in'}), 401

class CheckSessionResource(Resource):

    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return jsonify(user.to_dict()), 200
        return jsonify({'message': 'Unauthorized'}), 401

class ClearSession(Resource):

    def delete(self):
        session.clear()
        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                # Create a Response object and jsonify it
                article_json = jsonify(article.to_dict())
                return make_response(article_json, 200)
            else:
                return jsonify({'message': 'Article not found'}), 404

        return jsonify({'message': 'Maximum pageview limit reached'}), 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(UserResource, '/login')
api.add_resource(LogoutResource, '/logout')
api.add_resource(CheckSessionResource, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
