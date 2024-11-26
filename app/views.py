from app import app, db, admin, login_manager
from flask import render_template, redirect, url_for, flash, request, make_response
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import desc, asc
from .models import User, Product, Order, OrderItem, Review
from .forms import RegisterForm, LoginForm, AccountUpdateForm, CheckoutForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import json

## adding models to the admin page
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(OrderItem, db.session))
admin.add_view(ModelView(Review, db.session))

## get the current userid of logged in person
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# default route - homepage
@app.route('/')
def index():
    # Fetch specific featured products by IDs (to be changed depending on whats 'featured')
    featured_product_ids = [1, 20, 32]
    featured_products = Product.query.filter(Product.id.in_(featured_product_ids)).all()
    return render_template('index.html', products=featured_products)

# products route - displays all products to user 
@app.route('/products', methods=['GET'])
def products():
    # Fetch all products
    products = Product.query.all()
    # Manually construct the JSON structure
    products_json = []
    for product in products:
        products_json.append({
            "id": product.id,
            "name": product.name,
            "img": product.image, 
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
        })
    return render_template('products.html', products=products_json)

# product specifc route - generate a page for a specific product with its attributes 
@app.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = Product.query.get(product_id)
    # get reviews in order that they have been left in (earliest at top)
    reviews = Review.query.filter_by(product_id=product_id).order_by(desc(Review.created_at)).all()
    # Fetch user details for each review
    reviews_with_user_data = []
    for review in reviews: 
        reviews_with_user_data.append({
            "first_name": User.query.get(review.user_id).first_name,
            "last_name": User.query.get(review.user_id).last_name,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at})
    return render_template('product_detail.html', product=product, reviews=reviews_with_user_data)

# route for adding review to the database, returns response with name info
@app.route('/add-review', methods=['POST'])
@login_required # cannot add review without being logged in
def add_review():
    product_id = request.form.get('product_id')
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    # Create a new review
    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )
    ## add to db
    db.session.add(review)
    db.session.commit()
    # create response to be dynamically displayed
    response =  {    
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return response

# route for adding a product and quantity to basket cookies
@app.route('/add-to-basket', methods=['POST'])
def add_to_basket():
    # Get product ID and quantity from the form
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    # Retrieve the basket from cookies or initialize an empty basket
    basket_cookie = request.cookies.get('basket', '{}')
    basket = json.loads(basket_cookie)
    # Update the basket: increment quantity if product exists, otherwise add it
    if product_id in basket:
        basket[product_id] += quantity
    else:
        basket[product_id] = quantity
    # Save the updated basket to cookies
    response = make_response(redirect(url_for('basket')))
    response.set_cookie('basket', json.dumps(basket), timedelta(1))  # Cookie expires in 1 day
    return response
 
# basket route - page displaying basket info from basket cookies
@app.route('/basket', methods=['GET'])
def basket():
    # Retrieve the basket cookie and parse it
    basket_cookie = request.cookies.get('basket', '{}')
    basket = json.loads(basket_cookie)
    #fetch product details from the database using cookie
    products_in_basket = []
    for product_id, quantity in basket.items():
        product = Product.query.get(int(product_id))
        products_in_basket.append({
            'id': product.id,
            'name': product.name,
            'quantity': quantity,
            'price': f"{product.price:.2f}", 
            'stock': product.stock, 
            'total_price': f"{product.price * quantity:.2f}"})
    return render_template('basket.html', products=products_in_basket)

# route for updating basket cookies when quantity changed on site
@app.route('/update-basket', methods=['POST'])
def update_basket():
    # get the product, quantity from the POST request
    product_id = request.json.get('product_id')
    new_quantity = request.json.get('quantity')
    # Retrieve the basket
    basket_cookie = request.cookies.get('basket', '{}')
    basket = json.loads(basket_cookie)
    # Update basket logic
    if product_id in basket:
        if new_quantity <= 0:
            basket.pop(product_id)
        else:
            basket[product_id] = new_quantity
    # Update the cookie
    response = make_response({"message": "Basket updated"})
    response.set_cookie('basket', json.dumps(basket), timedelta(1)) # expires in 1 day
    return response

# route for deleting a product from basket cookies when deleted on basket page
@app.route('/delete-from-basket', methods=['POST'])
def delete_from_basket():
    # get relevent product id
    product_id = request.json.get('product_id')
    # Retrieve the basket
    basket_cookie = request.cookies.get('basket', '{}')
    basket = json.loads(basket_cookie)
    # Delete the product from the basket
    if product_id in basket:
        basket.pop(product_id)
    # Update the cookie
    response = make_response({"message": "Item removed from basket"})
    response.set_cookie('basket', json.dumps(basket), timedelta(1)) # expires in 1 day
    return response

# checkout route - page for displaying the final basket to user
@app.route('/checkout', methods=['GET', 'POST'])
@login_required # cant access checkout page unless logged in
def checkout():
    form = CheckoutForm() # for input validation
    # Fetch the basket from cookies
    basket_cookie = request.cookies.get('basket', '{}')
    basket = json.loads(basket_cookie)
    # If the basket is empty, redirect back to the basket page
    if not basket:
        flash("Your basket is empty! Add items before proceeding to checkout.")
        return redirect(url_for('basket'))
    # Fetch product details from the database
    basket_details = {}
    total_cost = 0
    for product_id, quantity in basket.items():
        product = Product.query.get(int(product_id))
        if product:
            basket_details[product_id] = {
                'name': product.name,
                'quantity': quantity,
                'price': product.price
            }
            total_cost += product.price * quantity
    return render_template('checkout.html', form=form, basket=basket_details, total_cost=total_cost)

# route for confirming a checkout - checks if the quantity is within bound of stock and updates db with order and orderItem entities
@app.route('/confirm-checkout', methods=['POST'])
@login_required # to confirm a checkout the user must be logged in
def confirm_checkout():
    # Retrieve the basket cookie and parse it
    basket_cookie = request.cookies.get('basket', '{}')
    basket = json.loads(basket_cookie)
    # Retrieve the submitted address
    address = request.form.get('address')
    # Validate stock availability and update stock levels
    for product_id, quantity in basket.items():
        product = Product.query.get(int(product_id))
        if not product or quantity > product.stock:
            flash(f"Product '{product.name}' is out of stock or exceeds available quantity. Please update your basket.")
            return redirect(url_for('basket'))
    # Deduct stock and create the order
    new_order = Order(user_email=current_user.email, address=address, date_ordered=datetime.now())
    db.session.add(new_order)
    db.session.flush()  # Ensure the order gets an ID
    ## create an orderItem for each item (with quantity) in order 
    for product_id, quantity in basket.items():
        product = Product.query.get(int(product_id))
        product.stock -= quantity
        order_item = OrderItem(order_id=new_order.id, product_id=product_id, quantity=quantity)
        db.session.add(order_item)
    # Commit changes to the database
    db.session.commit()
    # Clear the basket
    response = make_response(redirect(url_for('history')))
    response.set_cookie('basket', '', max_age=0)  # Clear the basket cookie
    flash("Checkout successful! Your order has been placed.")
    return response

#order history route - for displaying the user's order histroy and info back to them 
@app.route('/history', methods=['GET'])
@login_required # must be logged in
def history():
    # Fetch all orders for the logged-in user
    orders = Order.query.filter_by(user_email=current_user.email).order_by(Order.date_ordered.desc()).all()
    # Prepare data to send to the template - items and order info such as date address etc
    order_history = []
    for order in orders:
        # Fetch items for each order
        items = OrderItem.query.filter_by(order_id=order.id).all()
        order_items = []
        for item in items:
            product = Product.query.get(item.product_id)
            if product:
                order_items.append({
                    "name": product.name,
                    "quantity": item.quantity,
                    "price": product.price,
                    "total_price": product.price * item.quantity
                })
        order_history.append({
            "order_id": order.id,
            "date_ordered": order.date_ordered.strftime("%Y-%m-%d %H:%M:%S"),
            "address": order.address,
            "items": order_items,
            "total_value": sum(item['total_price'] for item in order_items)
        })
    return render_template('history.html', orders=order_history)

# login route - login page that uses requests to validate user info matches database
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if a user with the given email exists
        if User.query.filter_by(email=form.email.data).count() != 0:
            # Fetch the user for password verification
            user = User.query.filter_by(email=form.email.data).first()
            # Verify password
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=True)  # Log in the user
                flash('Logged in successfully.')
                return redirect(url_for('index')) # Redirect to the home page
        # If user doesn't exist or password is incorrect
        flash('Invalid email or password.')
    return render_template('login.html', form=form)

# logout route
@app.route('/logout')
def logout():
    logout_user()  # Ends the user session
    flash('You have been logged out.')
    return redirect(url_for('index'))  # Redirect to the home page

# register route - to create an instance of user in db, has input validation client + serverside
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).count() != 0:
            flash('Email already exists. Please choose another.')
            return redirect(url_for('register'))
        # Create and save the new user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        # add to database
        db.session.add(new_user)
        db.session.commit()  
        flash('Registration successful! Please log in.')
        return redirect(url_for('login')) # once account created go to login page
    return render_template('register.html', form=form)

# account route - to edit account info
@app.route('/account', methods=['GET', 'POST'])
@login_required # a user has to be signed in to use
def account():
    form = AccountUpdateForm()
    if form.validate_on_submit():
        # Require the old password for any change
        if not check_password_hash(current_user.password_hash, form.old_password.data):
            flash('Old password is required and must be correct to make changes.')
            return redirect(url_for('account'))
        # Update password if new password is provided
        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)
        # Check for email uniqueness if email is changed
        if form.email.data != current_user.email:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already exists. Please use a different email.')
                return redirect(url_for('account'))
        # Update user's name and email
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        # Commit changes to the db
        db.session.commit()
        flash('Your account has been updated successfully.', 'success')
        return redirect(url_for('account'))
    # populate form with user data
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('account.html', form=form)
