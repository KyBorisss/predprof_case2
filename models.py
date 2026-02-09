from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='ученик')
    grade = db.Column(db.String(10))
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    allergies = db.relationship('Allergy', backref='user', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic', foreign_keys='Order.user_id')
    feedbacks = db.relationship('Feedback', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic')
    prepared_meals = db.relationship('PreparedMeal', foreign_keys='PreparedMeal.prepared_by', backref='preparer',
                                     lazy='dynamic')
    served_orders = db.relationship('Order', foreign_keys='Order.served_by', backref='served_by_user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_active_subscription(self, meal_type):
        today = date.today()
        return Subscription.query.filter(
            Subscription.user_id == self.id,
            Subscription.meal_type == meal_type,
            Subscription.is_active == True,
            Subscription.end_date >= today
        ).first() is not None

    def get_active_subscription(self, meal_type):
        today = date.today()
        return Subscription.query.filter(
            Subscription.user_id == self.id,
            Subscription.meal_type == meal_type,
            Subscription.is_active == True,
            Subscription.end_date >= today
        ).first()

    def __repr__(self):
        return f'<User {self.username}>'


class Allergy(db.Model):
    __tablename__ = 'allergies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    allergen = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20))
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Allergy {self.allergen}>'


class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    meal_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer)
    allergens = db.Column(db.String(200))
    ingredients = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(200))

    orders = db.relationship('Order', backref='meal', lazy='dynamic')
    feedbacks = db.relationship('Feedback', backref='meal', lazy='dynamic')
    meal_ingredients = db.relationship('MealIngredient', backref='meal', lazy='dynamic')
    prepared_instances = db.relationship('PreparedMeal', backref='meal', lazy='dynamic')

    def __repr__(self):
        return f'<Meal {self.name}>'

    def get_required_ingredients(self, portions=1):
        ingredients = []
        for mi in self.meal_ingredients:
            if hasattr(mi, 'ingredient'):
                ingredients.append({
                    'id': mi.ingredient.id,
                    'name': mi.ingredient.ingredient,
                    'quantity_required': mi.quantity_required * portions,
                    'unit': mi.unit or mi.ingredient.unit,
                    'available': mi.ingredient.quantity,
                    'needed': max(0, (mi.quantity_required * portions) - mi.ingredient.quantity)
                })
        return ingredients

    def can_prepare(self, portions=1):
        for mi in self.meal_ingredients:
            required_amount = mi.quantity_required * portions
            if hasattr(mi, 'ingredient') and mi.ingredient.quantity < required_amount:
                return False
        return True

    def get_missing_ingredients(self, portions=1):
        missing = []
        for mi in self.meal_ingredients:
            if hasattr(mi, 'ingredient'):
                required_amount = mi.quantity_required * portions
                available = mi.ingredient.quantity
                if available < required_amount:
                    missing.append({
                        'id': mi.ingredient.id,
                        'name': mi.ingredient.ingredient,
                        'required': required_amount,
                        'available': available,
                        'needed': required_amount - available,
                        'unit': mi.unit or mi.ingredient.unit
                    })
        return missing

    def get_meal_type_display(self):
        types = {
            'завтрак': 'Завтрак',
            'обед': 'Обед',
            'напиток': 'Напиток'
        }
        return types.get(self.meal_type, self.meal_type)

    def get_available_quantity(self):
        today = date.today()
        total_quantity = 0

        for prepared in self.prepared_instances:
            if prepared.expiry_date and prepared.expiry_date >= today:
                total_quantity += prepared.quantity

        return total_quantity

    def is_available_for_order(self, quantity=1):
        if not self.is_available:
            return False

        available_quantity = self.get_available_quantity()
        return available_quantity >= quantity

    def get_prepared_meals_info(self):
        today = date.today()
        prepared_info = []

        for prepared in self.prepared_instances:
            if prepared.expiry_date and prepared.expiry_date >= today and prepared.quantity > 0:
                days_until_expiry = (prepared.expiry_date - today).days
                prepared_info.append({
                    'id': prepared.id,
                    'quantity': prepared.quantity,
                    'prepared_date': prepared.prepared_date,
                    'expiry_date': prepared.expiry_date,
                    'days_until_expiry': days_until_expiry,
                    'notes': prepared.notes
                })

        return prepared_info


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    meal_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    is_served = db.Column(db.Boolean, default=False)
    served_at = db.Column(db.DateTime)
    served_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    payment_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Order {self.id} - {self.user_id}>'


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback {self.rating} stars>'


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    min_quantity = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Inventory {self.ingredient}: {self.quantity}>'


class MealIngredient(db.Model):
    __tablename__ = 'meal_ingredients'

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))

    ingredient = db.relationship('Inventory', backref='meal_ingredients')

    def __repr__(self):
        return f'<MealIngredient meal:{self.meal_id} ingr:{self.ingredient_id}>'


class PreparedMeal(db.Model):
    __tablename__ = 'prepared_meals'

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    prepared_date = db.Column(db.Date, default=date.today, nullable=False)
    prepared_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    expiry_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<PreparedMeal {self.id}: {self.quantity} порций>'


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    meals_per_week = db.Column(db.Integer, default=5)
    used_meals = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Subscription {self.id}: {self.meal_type}>'

    @property
    def meals_remaining(self):
        return self.meals_per_week - self.used_meals

    @property
    def is_expired(self):
        return date.today() > self.end_date


class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(100), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    urgency = db.Column(db.String(20), default='средняя')
    status = db.Column(db.String(20), default='на рассмотрении')
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    requested_by_user = db.relationship('User', foreign_keys=[requested_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])
    ingredient_ref = db.relationship('Inventory', foreign_keys=[ingredient_id])

    def __repr__(self):
        return f'<PurchaseRequest {self.ingredient}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.title}>'