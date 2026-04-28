import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models.models import db, User, Product, Cart, CartItem, Order, OrderItem
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'realmadrid_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
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
                Product(name="Áo Real Madrid Sân Nhà 2024", price=1200000, description="Áo thi đấu chính thức mùa giải 2024-2025 với màu trắng truyền thống và họa tiết tinh tế.", image="/static/images/home_kit.png", category="Jersey"),
                Product(name="Áo Real Madrid Sân Khách 2024", price=1100000, description="Thiết kế hiện đại cho những trận đấu xa nhà, mang tông màu cam rực rỡ.", image="/static/images/away_kit.png", category="Jersey"),
                Product(name="Áo Real Madrid Thứ Ba 2024", price=1150000, description="Mẫu áo phá cách với tông màu xám than và họa tiết độc đáo.", image="https://images.unsplash.com/photo-1622279457486-62dcc4a4bd13?q=80&w=1000&auto=format&fit=crop", category="Jersey"),
                Product(name="Áo Thủ Môn Real Madrid (Xanh)", price=1300000, description="Trang phục dành cho những người gác đền của kền kền trắng.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="Jersey"),
                Product(name="Áo Training Real Madrid (Navy)", price=850000, description="Thoải mái cho những buổi tập luyện chuyên nghiệp.", image="https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1000&auto=format&fit=crop", category="Training"),
                Product(name="Áo Khoác Anthem Real Madrid", price=1850000, description="Áo khoác cao cấp mặc khi bước ra sân vận động.", image="https://images.unsplash.com/photo-1551854838-212c50b4c184?q=80&w=1000&auto=format&fit=crop", category="Training"),
                Product(name="Quần Short Real Madrid Home", price=550000, description="Đồng bộ hoàn hảo với áo sân nhà.", image="https://images.unsplash.com/photo-1591195853828-11db59a44f6b?q=80&w=1000&auto=format&fit=crop", category="Shorts"),
                Product(name="Tất Real Madrid 2024", price=250000, description="Chất liệu thoáng khí, hỗ trợ vận động tối ưu.", image="https://images.unsplash.com/photo-1582966232435-05842e61298c?q=80&w=1000&auto=format&fit=crop", category="Accessories"),
                Product(name="Bóng Real Madrid Pro 2024", price=950000, description="Bóng thi đấu đạt chuẩn quốc tế.", image="https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1000&auto=format&fit=crop", category="Accessories"),
                Product(name="Mũ Cap Real Madrid", price=450000, description="Phụ kiện không thể thiếu cho các Madridista.", image="https://images.unsplash.com/photo-1588850561407-ed78c282e89b?q=80&w=1000&auto=format&fit=crop", category="Accessories")
            ]
            db.session.bulk_save_objects(products)
            db.session.commit()

# --- Initialize Database ---
with app.app_context():
    seed_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
