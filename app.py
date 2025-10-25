from flask import Flask, render_template, request, flash,  redirect, url_for
from flask_login import LoginManager, current_user
from extensions import db
import os
from models import User
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Store.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init DB
    db.init_app(app)

    from models import User, Product

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.products import products_bp
    app.register_blueprint(products_bp)

    # Routes
    @app.route("/")
    def home():
        products = Product.query.limit(4).all()
        return render_template("home.html", user=current_user, products=products)

    @app.route("/about")
    def about():
        return render_template("about.html")
    
    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
           name = request.form.get("name")
           email = request.form.get("email")
           message = request.form.get("message")
           
           print(f"New Contact: {name}, {email}, {message}")
           flash("Your message has been sent successfully!", "success")
           return redirect(url_for("contact"))

        return render_template("contact.html")
    
    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        if not os.path.exists("Store.db"):
            db.create_all()
            if not User.query.filter_by(email="admin@estore.com").first():
                admin = User(
                    username="Admin",
                    email="admin@estore.com",
                    password_hash=generate_password_hash("admin123"),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created: admin@estore.com / admin123")

    app.run(debug=True)
