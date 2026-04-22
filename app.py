import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models.models import db, User, Product, Cart, CartItem, Order, OrderItem
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'realmadrid_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- Routes ---

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template('product_detail.html', product=product)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        # Create a cart for the new user
        new_cart = Cart(user_id=new_user.id)
        db.session.add(new_cart)
        db.session.commit()
        
        flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    return render_template('cart.html', cart=cart)

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if item:
        item.quantity += 1
    else:
        new_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
        db.session.add(new_item)
    
    db.session.commit()
    flash('Đã thêm vào giỏ hàng!', 'success')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = db.get_or_404(CartItem, item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart.items:
        flash('Giỏ hàng trống!', 'warning')
        return redirect(url_for('index'))
    
    total = sum(item.product.price * item.quantity for item in cart.items)
    order = Order(user_id=current_user.id, total_price=total, status='Paid (Simulated)')
    db.session.add(order)
    db.session.flush()
    
    for item in cart.items:
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(order_item)
        db.session.delete(item)
    
    db.session.commit()
    flash('Thanh toán thành công! Đơn hàng của bạn đang được xử lý.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return "Access Denied", 403
    products = Product.query.all()
    orders = Order.query.all()
    total_revenue = sum(o.total_price for o in orders)
    return render_template('admin.html', products=products, orders=orders, revenue=total_revenue)

# --- Admin CRUD ---
@app.route('/admin/add_product', methods=['POST'])
@login_required
def add_product():
    if current_user.role != 'admin': return "Access Denied", 403
    name = request.form.get('name')
    price = float(request.form.get('price'))
    desc = request.form.get('description')
    img = request.form.get('image')
    cat = request.form.get('category')
    
    new_product = Product(name=name, price=price, description=desc, image=img, category=cat)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete_product/<int:id>')
@login_required
def delete_product(id):
    if current_user.role != 'admin': return "Access Denied", 403
    product = db.session.get(Product, id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('admin'))

# --- Database Initialization ---
def seed_data():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password=bcrypt.generate_password_hash('admin123').decode('utf-8'), role='admin')
            db.session.add(admin_user)
            db.session.commit()
            # Create cart for admin too
            db.session.add(Cart(user_id=admin_user.id))
            db.session.commit()

        if not Product.query.first():
            products = [
                Product(name="Áo Real Madrid Sân Nhà 2024", price=1200000, description="Áo thi đấu chính thức mùa giải 2024-2025.", image="https://images.unsplash.com/photo-1622279457486-62dcc4a4bd13?q=80&w=1000&auto=format&fit=crop", category="home"),
                Product(name="Áo Real Madrid Sân Khách 2024", price=1100000, description="Thiết kế hiện đại cho những trận đấu xa nhà.", image="https://images.unsplash.com/photo-1622279457486-62dcc4a4bd13?q=80&w=1000&auto=format&fit=crop", category="away"),
                Product(name="Áo Training Real Madrid", price=850000, description="Thoải mái cho những buổi tập luyện.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="training"),
                Product(name="Áo Real Madrid Thứ Ba 2024", price=1150000, description="Mẫu áo phá cách với tông màu đen.", image="https://images.unsplash.com/photo-1622279457486-62dcc4a4bd13?q=80&w=1000&auto=format&fit=crop", category="away"),
                Product(name="Quần Short Real Madrid Home", price=500000, description="Đồng bộ với áo sân nhà.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="home"),
                Product(name="Tất Real Madrid 2024", price=200000, description="Chất liệu cao cấp, co giãn tốt.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="home"),
                Product(name="Áo Khoác Real Madrid Anthem", price=1800000, description="Áo khoác mặc lúc chào sân.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="training"),
                Product(name="Bóng Real Madrid Pro", price=950000, description="Bóng thi đấu tiêu chuẩn FIFA.", image="https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1000&auto=format&fit=crop", category="accessory"),
                Product(name="Khăn Choàng Real Madrid", price=350000, description="Khăn choàng cổ cho các fan trung thành.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="accessory"),
                Product(name="Mũ Real Madrid Cap", price=450000, description="Mũ lưỡi trai phong cách.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="accessory")
            ]
            db.session.bulk_save_objects(products)
            db.session.commit()

if __name__ == '__main__':
    seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
