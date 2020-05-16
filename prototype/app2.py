from flask import Flask, request
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
login = LoginManager(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = [User(0), User(1), User(2), User(3), User(4), User(5)]

@login.user_loader
def load_user(id):
    return User(int(id))

@login_required
@app.route('/', methods=['GET', 'POST'])
def login():
    # user_id = request.args.get('user_id')
    print(request.headers)
    return f'user: {current_user.id}'


if __name__ == "__main__":
    app.run(use_reloader=True, port=5001)