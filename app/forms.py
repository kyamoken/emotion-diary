from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('パスワード確認', validators=[DataRequired(), EqualTo('password')])

class DiaryForm(FlaskForm):
    date = DateField('日付', validators=[DataRequired()], default=date.today)
    content = TextAreaField('日記の内容', validators=[DataRequired(), Length(min=10)], 
                           render_kw={"rows": 10, "placeholder": "今日の出来事や気持ちを書いてください..."})

class SearchForm(FlaskForm):
    sentiment = SelectField('感情', choices=[('', '全て'), ('Positive', 'ポジティブ'), 
                                          ('Negative', 'ネガティブ'), ('Neutral', 'ニュートラル')])
    tag = StringField('タグ', render_kw={"placeholder": "タグで検索"})