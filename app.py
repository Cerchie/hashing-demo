from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from  models import connect_db, db, User, Feedback, Tweet
from forms import UserForm, TweetForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension
#--------------
#display routes
#--------------
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/tweets', methods=['GET', 'POST'])
def show_tweets(): 
    if "user_id" not in session:
        flash("please log in first", "danger")
        return redirect('/')
    form = TweetForm()
    all_tweets = Tweet.query.all()
    if form.validate_on_submit():
        text = form.text.data
        new_tweet = Tweet(text=text, user_id=session['user_id'])
        db.session.add(new_tweet)
        db.session.commit()
        flash('tweet created', "success")
        return redirect('/tweets')
    return render_template("tweets.html", form=form, tweets = all_tweets)
#-------------------
# DELETE ROUTES
#-------------------
@app.route('/tweets/<int:id>', methods=['POST'])
def delete_tweet(id):
    """delete tweet"""
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    tweet = Tweet.query.get_or_404(id)
    flash('you do not have permission to do that')
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('tweet deleted', "primary")
        return redirect('/tweets')
    
    return redirect('/tweets')

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    """delete feedback"""
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(id)
    flash('you do not have permission to do that')
    if tweet.user_id == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        flash('feedback deleted', "primary")
        return redirect('/users/<int:id>')
    
@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    """delete user"""
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    user = User.query.get_or_404(id)
    flash('you do not have permission to do that')
    if user.user_id == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        flash('feedback deleted', "primary")
        return redirect('/')
    

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try: 
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Pick another.')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully created your account!', "success")
        return redirect('/tweets')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(User, username, password)
        if user:
            flash(f'welcome back{user.username}!', "info")
            session['user_id'] = user.username
            return redirect('/users/<int:id>')
        else:
            form.username.errors = ['invalid username/password']

    return render_template("login.html", form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("successful logout")
    return redirect('/')

@app.route('/users/<int:id>')
def display_user(id):
    form = UserForm()
    password = form.password.data
    username = form.username.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    user = User.query.get_or_404(id)
    all_feedback = Feedback.query.all
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    if session['user_id'] == user.username:
        return render_template('user_info.html', user=user, email=email, first_name=first_name, last_name=last_name)