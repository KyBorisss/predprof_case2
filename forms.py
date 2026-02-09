from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from models import User


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    grade = StringField('Класс', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован.')


class AllergyForm(FlaskForm):
    allergen = StringField('Аллерген', validators=[DataRequired()])
    severity = SelectField('Степень', choices=[
        ('легкая', 'Легкая'),
        ('средняя', 'Средняя'),
        ('тяжелая', 'Тяжелая')
    ])
    notes = TextAreaField('Примечания')
    submit = SubmitField('Добавить')


class OrderForm(FlaskForm):
    meal_type = SelectField('Тип питания', choices=[
        ('завтрак', 'Завтрак (блюдо + напиток по желанию)'),
        ('обед', 'Обед (блюдо + напиток по желанию)')
    ], validators=[DataRequired()])
    meal_id = SelectField('Выберите основное блюдо', coerce=int, choices=[], validators=[DataRequired()])
    meal_date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    payment_method = SelectField('Способ оплаты', choices=[
        ('разовая', 'Разовая оплата'),
        ('абонемент', 'Абонемент (бесплатно)')
    ], validators=[DataRequired()])
    submit = SubmitField('Заказать')


class FeedbackForm(FlaskForm):
    meal_id = SelectField('Выберите блюдо', coerce=int, choices=[], validators=[DataRequired()])
    rating = IntegerField('Оценка', validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message='Оценка должна быть от 1 до 5')
    ])
    comment = TextAreaField('Комментарий', validators=[
        Length(max=500, message='Комментарий не должен превышать 500 символов')
    ])
    submit = SubmitField('Отправить отзыв')


class PurchaseRequestForm(FlaskForm):
    ingredient_id = SelectField('Продукт', coerce=int, choices=[], validators=[DataRequired()])
    quantity = FloatField('Количество', validators=[DataRequired(), NumberRange(min=0.1)])
    urgency = SelectField('Срочность', choices=[
        ('низкая', 'Низкая'),
        ('средняя', 'Средняя'),
        ('высокая', 'Высокая'),
        ('критичная', 'Критичная')
    ], default='средняя')
    notes = TextAreaField('Примечания')
    submit = SubmitField('Создать заявку')


class InventoryForm(FlaskForm):
    ingredient = StringField('Продукт', validators=[DataRequired()])
    quantity = FloatField('Количество', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Единица измерения', choices=[
        ('кг', 'кг'),
        ('л', 'л'),
        ('шт', 'шт')
    ])
    min_quantity = FloatField('Минимальный запас', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Сохранить')


class PrepareMealForm(FlaskForm):
    meal_id = SelectField('Блюдо', coerce=int, choices=[], validators=[DataRequired()])
    quantity = IntegerField('Количество порций', validators=[
        DataRequired(),
        NumberRange(min=1, max=100)
    ])
    expiry_date = DateField('Срок годности до', format='%Y-%m-%d')
    notes = TextAreaField('Примечания')
    submit = SubmitField('Приготовить')


class SubscriptionForm(FlaskForm):
    meal_type = SelectField('Тип питания', choices=[
        ('завтрак', 'Завтрак'),
        ('обед', 'Обед')
    ], validators=[DataRequired()])
    weeks = SelectField('Количество недель', choices=[
        (1, '1 неделя'),
        (2, '2 недели'),
        (4, '1 месяц (4 недели)'),
        (8, '2 месяца (8 недель)')
    ], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Купить абонемент')