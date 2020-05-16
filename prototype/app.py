from flask import Flask, request
from flask_login import LoginManager, UserMixin, current_user, login_user


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
login = LoginManager(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = [User(0), User(1), User(2), User(3), User(4), User(5)]

@login.user_loader
def load_user(id):
    print(f'load user call {id}')
    return users[int(id)]

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_id = int(request.args.get('user_id'))
    user = users[user_id]
    login_user(user)
    return f'<h1>user {user.id} loged in</h1>'

@app.route('/')
def home():
    return f'<h1>user {current_user.id} Home Page</h1>'




if __name__ == "__main__":
    app.run(use_reloader=True)