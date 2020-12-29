from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators, SubmitField
from wtforms.validators import InputRequired, Email, Length, DataRequired, EqualTo, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database_setup import Base, Conversations, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as Session
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from datetime import datetime
import random




app=Flask(__name__)
app.secret_key = 'super_secret_key' # secet key for session
# this scritkey could be created randomly by using ....
bootstrap = Bootstrap(app) # to facilate using bootstrap blocks
CORS(app) # to avoid error comming from CORS ex when js try to accesss data from another domain
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#------------------My Local DB
engine = create_engine(
    "mysql+pymysql://admin:Passw0rd@localhost:3306/chatdb?charset=utf8mb4")
#------------------My PythonAnywhere DB

#engine = create_engine(
#    "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format( username='abdelrahmankhali' , password='dbPass123' , hostname='abdelrahmankhalil.mysql.pythonanywhere-services.com' , databasename='abdelrahmankhali$chatdb'))
DBSession = sessionmaker(bind=engine)
SQLALCHEMY_DATABASE_URI = engine
session = DBSession()
session.close()
login_manager = LoginManager() # creat an object from LoginManager
login_manager.init_app(app)   # initiate it with my app
login_manager.login_view = 'login' # to redirect any not authorized page to login route




class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=80)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=1, max=80)])
    remember = BooleanField('remember me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Phone No.',
                        validators=[DataRequired(), Length(min=7, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    
    # for custom validation use function name validate_fiels name
    def validate_username(self, username):
        # use this method to access database
        session = DBSession()
        if  session.query(User).filter_by(name=username.data).first():
            session.close()
            raise ValidationError('That username is taken. Please choose another.')
            

    def validate_email(self, email):
        session = DBSession()
        if  session.query(User).filter_by(email=email.data).first():
            session.close()
            raise ValidationError('That email is taken. Please choose another.')
        
    
    


@login_manager.user_loader
def load_user(user_id):
    session = DBSession()
    a=session.query(User).get(int(user_id))
    session.close()
    return a
# here look like better than orginal 

@app.route("/register", methods=['GET', 'POST'])
def register():
    # check if the user is already signed in, then no need to view rigister page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        session = DBSession()
        if not session.query(User).filter_by(name=form.username.data).first():
            newUser = User(name=form.username.data,email=form.email.data, Password=form.password.data, phone=form.phone.data)
            session.add(newUser)
            session.commit()
            session.close()
            flash('Your account has been created! You are now able to log in', 'success ')
            return redirect(url_for('login'))
        else:
            session.close()
            flash('Username Taken', 'danger ')
            return render_template('register.html', title='Register', form=form)
    return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    session = DBSession()
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = session.query(User).filter_by(
                name=form.username.data).first()
        finally:
            if user:
                if user.Password == form.password.data:
                    login_user(user, remember=form.remember.data)
                    Session['user_id'] = user.id
                    session.close()
                    return redirect(url_for('home'))
            session.close()
            flash('Login Unsuccessful. Please check user and password', 'danger ')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route("/SaveChat", methods=['POST'])
@login_required
def SaveChat():
    if Session.get('user_id') is None:
        return redirect(url_for('login'))
# I think no need for this if as far @login_required do the same
    else:
        data_from_chat = request.get_json(force=True)
        print(data_from_chat)
        sent = data_from_chat["data"]["sent"]
        reply = data_from_chat["data"]["reply"]
        evaluation = int(data_from_chat["data"]["evaluation"])
        print("data from josn")
        #rf = request.form  # get posted data
        #print(rf)
        #for key in rf.keys():  # process data
         #   data = key
        #print(data)
        #data=data.replace('"','')
        
        #arr = data.split(',')  # Process data to array
        #print(arr)
        #ans = {  # process bot response elements to JSON Dictionary
         #   'r1': arr[1],
          #  'r2': arr[2],
           # 'r3': arr[3],
        #}
        session = DBSession()
        NewChat = Conversations(Question=sent, Answer=str(reply),  # Send processed data to database
                                Rating=evaluation,User_ID=Session.get('user_id'))
        session.add(NewChat)
        session.commit()  # save changes
        session.close()
        return jsonify({'Message': 'Successful'})


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
@login_required
def home():
    if Session.get('user_id') is None or not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        Page = 'Home'
        session = DBSession()
        connUser = session.query(User).filter(
            User.id == Session.get('user_id')).one()
        session.close()
        return render_template('home.html', page=Page, title='Users', conn=connUser,)


@app.route('/changepwd', methods=['GET', 'POST'])
def editPasswordUser():
    if Session.get('user_id') is None:
        return redirect(url_for('login'))
    else:
        Page='changepwd'
        session = DBSession()
        connUser = session.query(User).filter(
            User.id == Session.get('user_id')).one()
        userdata = session.query(User).filter(User.id == connUser.id).one()
        session.close()
        if request.method == 'POST':
            if request.form['Password']:
                userdata.Password = request.form['Password']
                session = DBSession()
                session.add(userdata)
                session.commit()
                flash('User Password Successfully Edited','success ')
                session.close()
                return redirect(url_for('home'))
        else:
            return render_template('editPassUser.html', conn=connUser, UserData=userdata, page=Page)



@app.route('/logout')
@login_required
def logout():
    Session['user_id'] = None
    session.close()
    logout_user()
    return redirect(url_for('login'))

# this solution to handel any request for non existing page
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('home'))


@app.route("/chat", methods=['GET', 'POST'])
@login_required
def Chathome():
    if Session.get('user_id') is None:
        return redirect(url_for('login'))

    else:
        Page = 'Chat'
        session = DBSession()
        connUser = session.query(User).filter(
            User.id == Session.get('user_id')).one()
        session.close()
        if request.method == 'GET':
            return render_template("chat.html", page=Page, title='ChatBot', conn=connUser)

        else:
            data_from_chat = request.get_json(force=True)
            user_msg = data_from_chat["data"]
            #rf = request.form
            #for key in rf.keys():
             #   data = key
            # send the list of bot response as json object with key :response
            temp_reply_from_botchat = ["ch'1"]
            bot_reply = temp_reply_from_botchat
            #return jsonify({'response': bot_reply})
            return jsonify(bot_reply)





if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000,use_reloader=False)