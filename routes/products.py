import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app import db
from models import Product, Order
from werkzeug.utils import secure_filename
from flask import session

products_bp = Blueprint("products", __name__, url_prefix="/products")

# ---------- Add Product ----------
@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        category = request.form.get("category")
        product_type = request.form.get("product_type")
        sizes = ",".join(request.form.getlist("sizes")) if request.form.getlist("sizes") else None
        color = request.form.get("color")
        stock = request.form.get("stock")

        # file upload handle
        image = request.files.get("image")
        image_filename = None
        if image:
            filename = secure_filename(image.filename)
            upload_path = os.path.join(current_app.root_path, "static/uploads", filename)
            image.save(upload_path)
            image_filename = filename

        new_product = Product(
            name=name,
            price=float(price),
            description=description,
            category=category,
            product_type=product_type,
            sizes=sizes,
            color=color,
            stock=stock,
            image_filename=image_filename
        )
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for("products.shop"))

    return render_template("add_product.html")



# ---------- Shop Page ----------
@products_bp.route("/shop")
def shop():
    # Get filter values from query params
    category = request.args.get("category")
    product_type = request.args.get("product_type")
    stock = request.args.get("stock")

    # Start query
    query = Product.query

    if category:
        query = query.filter_by(category=category)
    if product_type:
        query = query.filter_by(product_type=product_type)
    if stock:
        query = query.filter_by(stock=stock)

    products = query.all()
    return render_template("shop.html", products=products)

# ---------- Product Detail Page ----------
@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)




# ---------- Add to Cart ----------
@products_bp.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    # Fetch cart from session
    cart = session.get("cart", {})

    # Increment quantity if product already in cart
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    session["cart"] = cart
    flash("Product added to cart!", "success")
    return redirect(request.referrer or url_for("products.shop"))


# ---------- Update Cart ----------
@products_bp.route('/cart/update/<int:product_id>/<action>')
def update_cart(product_id, action):
    cart = session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        if action == 'increase':
            cart[pid] += 1
        elif action == 'decrease' and cart[pid] > 1:
            cart[pid] -= 1
    session['cart'] = cart
    return redirect(url_for('products.view_cart'))


# ---------- View Cart ----------
@products_bp.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    products = []

    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            products.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return render_template("cart.html", products=products, total=total)

# ---------- Remove from Cart ----------
@products_bp.route("/remove-from-cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session["cart"] = cart
        flash("Product removed from cart.", "info")
    return redirect(url_for("products.view_cart"))

# ---------- Checkout Page ----------
@products_bp.route("/checkout")
def checkout():
    cart = session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            products.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return render_template("checkout.html", products=products, total=total)


# ---------- Place Order ----------
@products_bp.route("/place-order", methods=["POST"])
def place_order():
    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty!", "danger")
        return redirect(url_for("products.shop"))

    fullname = request.form.get("fullname")
    email = request.form.get("email")
    address = request.form.get("address")
    phone = request.form.get("phone")
    payment = request.form.get("payment")

    # Calculate total
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * quantity

    # Save order in DB
    new_order = Order(
        fullname=fullname,
        email=email,
        address=address,
        phone=phone,
        payment=payment,
        total=total
    )
    db.session.add(new_order)
    db.session.commit()

    # Clear cart after order
    session["cart"] = {}

    flash("Your order has been placed successfully!", "success")
    return redirect(url_for("products.shop"))