from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, DiaryEntry
from app.forms import LoginForm, RegisterForm, DiaryForm, SearchForm
from ai.sentiment import sentiment_analyzer
from ai.tagging import auto_tagger
from datetime import datetime

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('ユーザー名またはパスワードが間違っています。')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('このユーザー名は既に使用されています。')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('このメールアドレスは既に登録されています。')
            return render_template('register.html', form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Main application routes
@main.route('/')
@login_required
def index():
    search_form = SearchForm()
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.date.desc()).limit(10).all()
    return render_template('index.html', entries=entries, search_form=search_form)

@main.route('/write', methods=['GET', 'POST'])
@login_required
def write_diary():
    form = DiaryForm()
    if form.validate_on_submit():
        # Analyze sentiment and extract tags
        sentiment = sentiment_analyzer.analyze_sentiment(form.content.data)
        tags = auto_tagger.extract_tags(form.content.data)
        
        entry = DiaryEntry(
            user_id=current_user.id,
            date=form.date.data,
            content=form.content.data,
            sentiment=sentiment,
            tags=', '.join(tags) if tags else None
        )
        db.session.add(entry)
        db.session.commit()
        flash(f'日記を保存しました。感情: {sentiment}')
        return redirect(url_for('main.index'))
    return render_template('write.html', form=form)

@main.route('/search')
@login_required
def search():
    form = SearchForm()
    entries = []
    
    if request.args.get('sentiment') or request.args.get('tag'):
        query = DiaryEntry.query.filter_by(user_id=current_user.id)
        
        if request.args.get('sentiment'):
            query = query.filter(DiaryEntry.sentiment == request.args.get('sentiment'))
        
        if request.args.get('tag'):
            tag = request.args.get('tag')
            query = query.filter(DiaryEntry.tags.contains(tag))
        
        entries = query.order_by(DiaryEntry.date.desc()).all()
    
    return render_template('search.html', form=form, entries=entries)

@main.route('/entry/<int:id>')
@login_required
def view_entry(id):
    entry = DiaryEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('entry.html', entry=entry)

# PWA用のstatic配信
@main.route('/static/<path:filename>')
def static_files(filename):
    from flask import send_from_directory
    return send_from_directory('app/static', filename)