from mvc import app
from flask import Flask , request , jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from .models import User,News,db
from functools import wraps
from newsapi import NewsApiClient
import os

def token_needed(f):
    @wraps(f)
    def decorated(*argw, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid'})

        return f(*args, **kwargs)
    
    return decorated

class Showall(MethodView):
    @token_needed
    def get(self,current_user):
        
        if not current_user.admin:
            return jsonify({'message' : 'Cannot perform the required function'})
        
        users = User.query.all()
        output = []
        for use in users:
            user_details = {}
            user_details['public_id'] = use.public_id
            user_details['name'] = use.name
            user_details['password'] = use.password
            output.append(user_details)
            
         return jsonify({'users' : output})

class Createuser(MethodView):
    def post(self):
        
        if not current_user.admin:
            return jsonify({'message' : 'Cannot perform the required function'})

        data = request.get_json()
        
        if User.query.filter_by(name = data['username']).first() is not None:
            return jsonify({'message' : 'Username already Exist'})
        
        if len(data['password'])<8:
            return jsonify({'message' : 'minimum length of the password is 8'})
        

        hash_password = generate_password_hash(data['password'] , method = 'sha256')

        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hash_password, admin=False)
        db.session.add(new_user)
        db.session.commit()
    
        return jsonify({'message' : 'New user created!'})

class Editdetails(MethodView):
    @token_needed
    def get(self,current_user,public_id):

        if not current_user.admin:
            return jsonify({'message' : 'Cannot do the function'})

        user = User.query.filter_by(public_id = public_id).first()
        if not in user:
            return jsonify({'message' : 'User not found'})

        user_info = {}
        user_info['public_id'] = user.public_id
        user_info['name'] = user.name
        user_info['password'] = user.password
        user_info['username'] = user.username
        user_info['email'] = user.email
        output.append(user_info)

        return jsonify({'user' : user_info})

    
    @token_needed
    def put(self):
        
        token = request.headers[''x-access-token']
        data = jwt.decode(token, app.config['SECRET_KEY'])

        user = User.query.filter_by(public_id = public_id).first()

        if not in user:
            return jsonify({'message' : 'No user found'})
        
        info = request.get_json()
        user.email = data["email"]
        curr_pass = data["curr_pass"]
                                
        if check_password_hash(user.password , curr_pass):
            user.password = data["new_pass"]
        
        else:
            return jsonify({'message' : 'Enter correct current Password'})
        
        db.session.commit()

        return jsonify({'message' : 'The User is Promoted'})

    @token_needed
    def delete(current_user,public_id):

        if not current_user.admin:
            return jsonify({'message' : 'Cannot perform the required function'})


        user = User.query.filter_by(public_id = public_id).first()

        if not in user:
            return jsonify({'message' : 'No user found'})

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message' : 'The User Has been deleted'})

class login():
    def post(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Cannot Verify')

        user = User.query.filter_by(name=auth.username).first()

        if not user:
            return make_response('Cannot Verify')

        if check_password_hash(user.password , auth.password):
            token = jwt.encode({'public_id' : user.public_id , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30), app.config['SECRET_KEY']})

            return jsonify({'token' : token.decode('UTF-8')})

        return make_response('Cannot Verify')


class News(MethodView):
    @token_needed
    def get(self,current_user):
        if not current_user.admin:
            return jsonify({'message': 'Cannot perform that function!'})

        newsapi = NewsApiClient(api_key=os.environ.get("APIKEY"))
        data=["sports","business","technology","entertainment"]
        for k in data:
         for i in range(1,10):
            top_headlines = newsapi.get_top_headlines(category=k,country='in', page=i)
            articles=top_headlines['articles']
            for i in range(len(articles)):
                myarticle=articles[i]
                new_article = News(author=myarticle['author'],title=myarticle['title'],description=myarticle['description'],url=myarticle['url'],content=myarticle['content'],category=k,date=datetime.date.today())
                db.session.add(new_article)
        db.session.commit()

        return jsonify({"message": "News Stored in Database"})

class Category(MethodView):
    @token_needed
    def get(self,num):
        category=request.args['category']
        news=News.query.filter_by(category=category,date=datetime.date.today())
        output=[]
        for new in news:
            news_info={}
            news_info['author'] = new.author
            news_info['title'] = new.title
            news_info['description'] = new.description
            news_info['url'] = new.url
            news_info['content'] = new.content
            output.append(news_info)
        start = (num * 10) - 9
        end = (num * 10) + 1
        return jsonify({"message": output[start:end]})

