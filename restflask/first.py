from flask import Flask , request , jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from newsapi import NewsApiClient
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password123@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    pid = db.Column(db.Integer,primary_key=True)
    public_id = db.Column(db.Text, unique=True)
    name = db.Column(db.Text,nullable=False)
    password = db.Column(db.Text,nullable=False)
    admin = db.Column(db.Boolean)

class News(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title =  db.Column(db.Text)
   description =  db.Column(db.Text)
   url =  db.Column(db.Text)
   content = db.Column(db.String(1000))
   category = db.Column(db.Text)

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

        return f(current_user , *args, **kwargs)
    
    return decorated

@app.route('/user', methods=['GET'])
@token_needed
def show_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform the required function'})

    users = User.query.all()
    output = []
    for use in users:
        user_details = {}
        user_details['public_id'] = use.public_id
        user_details['name'] = use.name
        user_details['password'] = use.password
        user_details['admin'] = use.admin
        output.append(user_details)

    return jsonify({'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
@token_needed
def show_required_user(current_user,public_id):
    
    if not current_user.admin:
        return jsonify({'message' : 'Cannot do the function'})

    user = User.query.filter_by(public_id = public_id).first()
    if not in user:
        return jsonify({'message' : 'User not found'})

    user_info = {}
    user_info['public_id'] = user.public_id
    user_info['name'] = user.name
    user_info['password'] = user.password
    user_info['admin'] = user.admin
    output.append(user_info)

    return jsonify({'user' : user_info})

@app.route('/user' , methods=['POST'])
@token_needed
def create_user(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform the required function'})

    data = request.get_json()

    hash_password = generate_password_hash(data['password'] , method = 'sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hash_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message' : 'New user created!'})

@app.route('/user/<public_id>', methods=['PUT'])
@token_needed
def promote_user(current_user,public_id):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform the required function'})

    user = User.query.filter_by(public_id = public_id).first()

    if not in user:
        return jsonify({'message' : 'No user found'})
    
    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'The User is Promoted'})

@app.route('/user/<public_id>' , methods=['DELETE'])
@token_needed
def delete_user(current_user,public_id):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform the required function'})


    user = User.query.filter_by(public_id = public_id).first()

    if not in user:
        return jsonify({'message' : 'No user found'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The User Has been deleted'})

@app.route('/login')
def login():
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


@app.route('/news',methods=['GET'])
@token_needed
def newsapp(current_user):
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

@app.route('/category/<int:num>',methods=['GET'])
def category(num):
    category=request.args['category']
    news=News.query.filter_by(category=category,date=datetime.date.today())
    output=[]
    for new in news:
        news_data={}
        news_data['author'] = new.author
        news_data['title'] = new.title
        news_data['description'] = new.description
        news_data['url'] = new.url
        news_data['content'] = new.content
        output.append(news_data)
    start = (num * 10) - 9
    end = (num * 10) + 1
    return jsonify({"message": output[start:end]})

if __name__ == '__main__':
    app.run(debug=True)
