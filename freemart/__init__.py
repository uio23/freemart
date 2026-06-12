from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from flask_login import LoginManager, AnonymousUserMixin, current_user
from flask_mail import Mail

import os


db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN')

    from .auth import auth
    from .market import market
    from .user import user
    from .income import income

    app.register_blueprint(user)
    app.register_blueprint(market)
    app.register_blueprint(auth)
    app.register_blueprint(income)


    mail.init_app(app)

    from .models import User, Product, Message

    db.init_app(app)
    create_database(app)


    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    @app.route("/")
    @app.route("/home")
    def home_page():
        if current_user.is_authenticated:
            return redirect(url_for("user.profile_page", username=current_user.username))
        return render_template("home.html", user=current_user)


    from .models import Message

    socketio = SocketIO(app)
    @socketio.on('message')
    def message(data):
        if db.session.query(Message).count() > 50:
            oldestMessage = db.session.query(Message).first()
            db.session.delete(oldestMessage)

        if data["auth"]:
            print(f"\n\n > {data['username']} connected to the chatroom. \n\n")
        elif data["msg"] == '':
            pass
        else:
            socketio.send(data)
            message = Message(msg=data['msg'], username=data["username"])
            db.session.add(message)
        db.session.commit()


    return app


def create_database(app):
    with app.app_context():
        db.create_all()
