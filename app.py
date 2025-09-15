from flask import Flask, render_template
from flask_login import LoginManager, current_user
from extensions import db   # db ab yahan se import hoga
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Store.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    from models import User

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Add Products
    from routes.products import products_bp
    app.register_blueprint(products_bp)


    # Home Route
    from models import User, Product   # Product bhi import karlo

    @app.route("/")
    def home():
          products = Product.query.limit(4).all()  # sirf 4 featured products
          return render_template("home.html", user=current_user, products=products)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        if not os.path.exists("Store.db"):
            db.create_all()
    app.run(debug=True)
