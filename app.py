from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from  models import connect_db, db, User, Feedback, Tweet
from forms import UserForm, TweetForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'secret1')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
print('**********************')
print('**********************')
print('**********************')
print('**********************')
print(app.config['SECRET_KEY'])


from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy import select

some_engine = create_engine(...)

@event.listens_for(some_engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        # "branch" refers to a sub-connection of a connection,
        # we don't want to bother pinging on these.
        return

    # turn off "close with result".  This flag is only used with
    # "connectionless" execution, otherwise will be False in any case
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        # run a SELECT 1.   use a core select() so that
        # the SELECT of a scalar value without a table is
        # appropriately formatted for the backend
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        # catch SQLAlchemy's DBAPIError, which is a wrapper
        # for the DBAPI's exception.  It includes a .connection_invalidated
        # attribute which specifies if this connection is a "disconnect"
        # condition, which is based on inspection of the original exception
        # by the dialect in use.
        if err.connection_invalidated:
            # run the same SELECT again - the connection will re-validate
            # itself and establish a new connection.  The disconnect detection
            # here also causes the whole connection pool to be invalidated
            # so that all stale connections are discarded.
            connection.scalar(select([1]))
        else:
            raise
    finally:
        # restore "close with result"
        connection.should_close_with_result = save_should_close_with_result
        
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

@app.route('/users/<int:id>')
def display_user(id):
    user = User.query.get_or_404(id)
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    if session['user_id'] == user.id:
        return render_template('user_info.html', user=user)
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
    if feedback.user.id == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        flash('feedback deleted', "primary")
    return redirect(f'/users/{user.id}')
    
@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    """delete user"""
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    user = User.query.get_or_404(id)
    flash('you do not have permission to do that')
    if user.id == session['user_id']:
        db.session.delete(user)
        db.session.commit()
        flash('feedback deleted', "primary")
        return redirect('/')
    
#-------------
#other user routes, register, login and logout
#-------------
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form2 = UserForm()
    if form2.validate_on_submit():
        username = form2.username.data
        password = form2.password.data
        email = form2.email.data
        first_name = form2.first_name.data
        last_name = form2.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try: 
            db.session.commit()
        except IntegrityError:
            form2.username.errors.append('Username taken. Pick another.')
            return render_template('register.html', form2=form2)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully created your account!', "success")
        form2 = FeedbackForm()
        
    return render_template('register.html', form2=form2)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    username = form.username.data
    password = form.password.data
    user = User.authenticate(User, username, password)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(User, username, password)
        if user:
            flash(f'welcome back{user.username}!', "info")
            session['user_id'] = user.id
            return redirect(f"/users/{user.id}")
        else:
            form.username.errors = ['invalid username/password']

    return render_template("login.html", form=form, user=user)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("successful logout")
    return redirect('/')

#--------------------------------
# NEW FEEDBACK ROUTES
#--------------------------------

# @app.route('/users/<int:id>/feedback/add', methods=['GET', 'POST'])
# def display_feedback_form(id):
#     form2 = FeedbackForm()
#     user = User.query.get_or_404(id)
#     if 'user_id' not in session:
#         flash("Please log in first", "danger")
#         return redirect('/login')
#     if user.id == session['user_id']:
#         if form2.validate_on_submit():
#             title = form2.title.data
#             content = form2.content.data
#             username = form2.username.data
#             feedback = Feedback(
#                 title=title,
#                 content=content,
#                 username=username,
#             )

#             db.session.add(feedback)
#             db.session.commit()
#             return redirect(f"/users/{id}")
#     return render_template('add_feedback.html', form2= form2, user=user)

@app.route('/users/<int:id>/feedback/add', methods=['GET', 'POST'])
def display_feedback_form(id):
    form2 = FeedbackForm()
    user = User.query.get_or_404(id)
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    print('***', user.id == session['user_id'])
    if user.id == session['user_id']:
        if form2.validate_on_submit():
            title = form2.title.data
            content = form2.content.data
            username = form2.username.data

            feedback = Feedback(
                title=title,
                content=content,
                username=username,
            )

            db.session.add(feedback)
            db.session.commit()
            return redirect(f"/users/{id}")
    
    return render_template('add_feedback.html', form2= form2, user=user)



@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def display_feedback_update_form(id):
    form2 = FeedbackForm()
    title = form2.title.data
    content = form2.content.data
    username = form2.username.data
    feedback = Feedback.query.get_or_404(id)
    db.session.add(feedback)
    db.session.commit()
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    if feedback.user.id == session['user_id']:
       form2 = FeedbackForm()
    return render_template("base.html")
