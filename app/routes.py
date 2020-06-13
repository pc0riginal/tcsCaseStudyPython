from app import app,mongo
from flask import render_template,redirect,url_for,flash,session
from app.forms import LoginForm

user = mongo.db['user']

@app.route('/')
@app.route('/index')
def index():
    if not session.get("username"):
        return redirect('/login')
    return render_template("index.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get("username"):
        return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
        userData = user.find_one({"username":form.username.data})
        if userData and userData['password'] == form.password.data:
            flash(f"{userData['username']},you are successfully logged in!","success")
            session['username'] = userData['username']
            return redirect("/index",)
        else:
            flash("sorry try again!","danger")
    return render_template("login.html",login=True,title="Login",form=form)        

