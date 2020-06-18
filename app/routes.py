from app import app,mongo
from flask import render_template,redirect,url_for,flash,session,request
from app.forms import LoginForm,CreateAccount,DeleteAccount,CreateCustomer,UpdateCustomer,Deposit,Withdraw,Transfer,Statement
import random
import string
from datetime import date
import datetime
import dateutil.parser as parser

user = mongo.db['user']
customer = mongo.db['customer']
account = mongo.db['account']
state = mongo.db['statement']
cusStatus = mongo.db['customerStatus']
accStatus = mongo.db['accountStatus']

@app.route('/')
@app.route('/index')
def index():
    if not session.get("username"):
        return redirect('/login')
    return render_template("index.html",index=True)

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
            session['type'] = userData['type']
            return redirect("/index",)
        else:
            flash("user not exist!","danger")
    return render_template("login.html",login=True,title="Login",form=form)        


@app.route("/create_account",methods=['GET','POST'])
def create_account():
    if not session.get("username"):
        return redirect('/login')
    print(date)
    form = CreateAccount()
    if form.validate_on_submit():
        customerData = customer.find_one({"customer_id":form.customerID.data})
        if customerData:
            account_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) 
            account.insert_one({"customer_id":form.customerID.data,"account_id":account_id,"account_type":form.account_type.data,"amount":form.amount.data})
            customer.update_one({"customer_id":form.customerID.data},{"$push":{"accounts":account_id}})
            accStatus.insert_one({"customer_id":form.customerID.data,"account_id":account_id,
            "account_type":form.account_type.data,"status":"active","message":"created","last_updated":date.today().strftime("%Y-%m-%d")})
            flash(f"{customerData['name']} Thank you for creating {form.account_type.data} account with amount={form.amount.data}","success")
        else:
            flash(f"customer not found!","danger")
    return render_template("create_account.html",create_account=True,form=form)

@app.route('/viewAccount',methods=['GET','POST'])
@app.route('/viewAccount/<view>',methods=['GET','POST'])
def viewAccount(view=None):
    if not session.get("username"):
        return redirect('/login')
    form = DeleteAccount()
    if form.validate_on_submit():
        one_customer = customer.find_one({"customer_id":form.customerID.data})
        if one_customer:
            return redirect(url_for("view_account",cid=form.customerID.data,view=view))
        else:
            flash("customer not exist")
    return render_template("delete_account.html",form=form,delete_account=True,view=view)

@app.route("/view_account",methods=['GET','POST'])
@app.route("/view_account/<cid>",methods=['GET','POST'])
def view_account(cid=None,view=None):
    if not session.get("username"):
        return redirect('/login')
    if cid:
        accounts = account.find({"customer_id":cid})
    return render_template("delete_account.html",accounts=accounts,cid=cid,view_account=True,view=request.args.get('view'))

@app.route("/delete_account",methods=['GET','POST'])
def delete_account():
    if not session.get("username"):
        return redirect('/login')
    aid = request.args.get('aid')
    cid = request.args.get('cid')
    view = request.form.get('view')
    print(view)
    if aid:
        account.delete_one({'account_id':aid})
        accStatus.insert_one({"customer_id":cid,"account_id":aid,
        "account_type":"saving","status":"deactive","message":"deleted","last_updated":date.today().strftime("%Y-%m-%d")})
        flash("successfully deleted","success")
        return redirect(url_for('view_account',cid=cid,view=view))
    return render_template("delete_account.html",delete_account=True,view=view)


@app.route("/create_customer",methods=['GET','POST'])
@app.route("/create_customer/<cid>",methods=['GET','POST'])
def create_customer(cid=None):
    if not session.get("username"):
        return redirect('/login')
    # print(update)
    form = CreateCustomer()
    if cid:
        customerData = customer.find_one({"customer_id":cid})
        form.customerID.data = cid
        form.name.data = customerData['name']
        form.age.data = customerData['age']
        form.addressline1.data = customerData['addressline1']
        form.addressline2.data = customerData['addressline2']
        form.city.data = customerData['city']
        form.state.data = customerData['state']
    if form.validate_on_submit():
        customerData = customer.find_one({"customer_id":form.customerID.data})
        if not customerData and cid==None:
            customer.insert_one({"customer_id":form.customerID.data,"name":form.name.data,"age":form.age.data,"addressline1":form.addressline1.data,
            "addressline2":form.addressline2.data,"city":form.city.data,"state":form.state.data,"accounts":[]})
            cusStatus.insert_one({"customer_id":form.customerID.data,"status":"active","message":"created","last_updated":date.today().strftime("%Y-%m-%d")})
            flash(f"{form.name.data} your account successfully created!","success")
        elif customerData and cid:
            print("hi")
            data = request.form
            customer.update_one({"_id":customerData['_id']},{"$set":{"name":data.get('name'),"age":data.get('age'),"addressline1":data.get('addressline1'),
            "addressline2":data.get('addressline2'),"city":data.get('city'),"state":data.get('state')}})
            cusStatus.insert_one({"customer_id":form.customerID.data,"status":"active","message":"updated","last_updated":date.today().strftime("%Y-%m-%d")})
            flash(f"{form.name.data} your account successfully updated!","success")
            return redirect('/update_customer')
        else:
            flash(f"{form.name.data} sorry try again!","danger")
    return render_template("create_customer.html",create_customer=True,form=form,cid=cid)
    
@app.route("/view_customer",methods=['GET','POST'])
@app.route("/view_customer/<view>",methods=['GET','POST'])
def view_customer(view=None):
    if not session.get("username"):
        return redirect('/login')
    existingCustomers = customer.find()
    return render_template("delete_customer.html",existingCustomers=existingCustomers,delete_customer=True,view=view)

@app.route("/deleteCustomer",methods=['GET','POST'])
def deleteCustomer():
    if not session.get("username"):
        return redirect('/login')
    customer_id = request.form.get('customer_id')
    show = request.form.get('show')
    delete = request.form.get('delete')
    view = request.form.get('view')
    if show=='True':
        one_customer = customer.find_one({"customer_id":customer_id})
        # print(one_customer)
        # print(one_customer['accounts'])
        accounts = account.find({"account_id":{"$in":one_customer['accounts']}})
    elif delete=='True':
        customer.delete_one({"customer_id":customer_id})
        account.delete_many({"customer_id":customer_id})
        cusStatus.insert_one({"customer_id":customer_id,"status":"deactive","message":"deleted","last_updated":date.today().strftime("%Y-%m-%d")})
        flash(f"{customer_id} deleted successfully ","danger")
        return redirect("/view_customer")
    else:
        return redirect("/view_customer")
    return render_template("delete_customer.html",delete=True,one_customer=one_customer,accounts=accounts,view=view)

@app.route('/update_customer',methods=['GET','POST'])
def update_customer():
    if not session.get("username"):
        return redirect('/login')
    form = UpdateCustomer()
    if form.validate_on_submit():
        one_customer = customer.find_one({"customer_id":form.customerID.data})
        if not one_customer:
            flash("customer not exist!","danger")
            return redirect('/update_customer')
        else:
            return redirect(url_for('create_customer',cid=form.customerID.data))
    return render_template("update_customer.html",update_customer=True,form=form)
    

@app.route('/deposit',methods=['GET','POST'])
def deposit():
    if not session.get("username"):
        return redirect('/login')
    form = Deposit()
    form.customerID.data = request.args.get('cid')
    form.accountID.data = request.args.get('aid')
    form.amount.data = request.args.get('amount')
    if form.validate_on_submit():
        accountData = account.find_one({"account_id":form.accountID.data})
        if accountData:
            account.update_one({"account_id":form.accountID.data},{"$inc":{"amount":form.depositAmount.data}})
            statement_id = ''.join([random.choice(string.digits) for n in range(9)]) 
            state.insert_one({'customer_id':form.customerID.data,'account_id':form.accountID.data,"transaction_id":statement_id,
            "action":"deposit","amount":form.depositAmount.data,"date":date.today().strftime("%Y-%m-%d")})
            flash(f"{form.depositAmount.data} amount deposit into this account={form.accountID.data}!","success")
            return redirect(url_for('view_account',cid=form.customerID.data,view=True))
        else:
            flash("account not exist!","danger")
    return render_template("deposit.html",form=form)

@app.route('/withdraw',methods=['GET','POST'])
def withdraw():
    if not session.get("username"):
        return redirect('/login')
    form = Withdraw()
    form.customerID.data = request.args.get('cid')
    form.accountID.data = request.args.get('aid')
    form.amount.data = request.args.get('amount')
    if form.validate_on_submit():
        accountData = account.find_one({"account_id":form.accountID.data})
        if accountData:
            withdrawAmount = form.withdrawAmount.data*-1
            account.update_one({"account_id":form.accountID.data},{"$inc":{"amount": withdrawAmount}})
            statement_id = ''.join([random.choice(string.digits) for n in range(9)]) 
            state.insert_one({'customer_id':form.customerID.data,'account_id':form.accountID.data,"transaction_id":statement_id,
            "action":"withdraw","amount":form.withdrawAmount.data,"date":date.today().strftime("%Y-%m-%d")})
            flash(f"{form.withdrawAmount.data} amount withdraw from this account={form.accountID.data}!","success")
            return redirect(url_for('view_account',cid=form.customerID.data,view=True))
        else:
            flash("account not exist!","danger")
    return render_template("withdraw.html",form=form)

@app.route('/transfer',methods=['GET','POST'])
def transfer():
    if not session.get("username"):
        return redirect('/login')
    form = Transfer()
    form.customerID.data = request.args.get('cid')
    form.accountID.data = request.args.get('aid')
    form.amount.data = request.args.get('amount')
    if form.validate_on_submit():
        accountData = account.find_one({"account_id":form.accountID.data})
        targetAccountData = account.find_one({"account_id":form.targetAccount.data})
        if accountData and targetAccountData:
            transferAmount = form.transferAmount.data*-1
            account.update_one({"account_id":form.accountID.data},{"$inc":{"amount": transferAmount}})
            account.update_one({"account_id":form.targetAccount.data},{"$inc":{"amount": form.transferAmount.data}})
            statement_id = ''.join([random.choice(string.digits) for n in range(9)]) 
            state.insert_one({'customer_id':form.customerID.data,'account_id':form.accountID.data,"transaction_id":statement_id,
            "action":"transfer","amount":form.transferAmount.data,"date":date.today().strftime("%Y-%m-%d")})
            flash(f"{form.transferAmount.data} amount transfer from this account={form.accountID.data}!","success")
            return redirect(url_for('view_account',cid=form.customerID.data,view=True))
        else:
            flash("account not exist!","danger")
    return render_template("transfer.html",form=form)

@app.route('/statement',methods=['GET','POST'])
def statement():
    # if not session.get("username"):
    #     return redirect('/login')
    maxdate = date.today()
    # strtime = maxdate.strftime("%Y-%m-%d")
    statements=None
    request.form.get('start')
    form = Statement()
    if form.validate_on_submit():
        if form.nTransaction.data == "None":
            if request.form.get('start') and request.form.get('end'):
                accountOne = account.find_one({"account_id":form.accountID.data})
                if accountOne:
                    statements = state.find({"account_id":form.accountID.data,"date":{"$gte":request.form.get('start'),"$lte":request.form.get('end')}})
                else:
                    flash("please enter valid account id","danger")
            else:
                flash("Please select ntransaction or date","danger")
        elif request.form.get('start')==" " or request.form.get('end')==" ":
            if form.nTransaction.data:
                accountOne = account.find_one({"account_id":form.accountID.data})
                if accountOne:
                    statements = state.find({"account_id":form.accountID.data}).sort([("date",1)]).limit(int(form.nTransaction.data))
                else:
                    flash("please enter valid account id","danger")
            else:
                flash("Please select ntransaction or date","danger") 
        elif form.nTransaction.data:
            accountOne = account.find_one({"account_id":form.accountID.data})
            if accountOne:
                statements = state.find({"account_id":form.accountID.data}).sort([("date",1)]).limit(int(form.nTransaction.data))
            else:
                flash("please enter valid account id","danger")

    return render_template('statement.html',statement=True,form=form,maxdate=maxdate,statements=statements)


@app.route("/logout",methods=['GET','POST'])
def logout():
    if not session.get('username'):
        return redirect('/login')
    session.pop('username')
    return redirect('/login')

@app.route('/customer_statement',methods=['GET','POST'])
def customer_statement():
    if not session.get('username'):
        return redirect('/login')
    customerStatements = cusStatus.find()
    return render_template('customer_statement.html',customer_statement=True,customerStatements=customerStatements)

@app.route('/account_statement',methods=['GET','POST'])
def account_statement():
    if not session.get('username'):
        return redirect('/login')
    accountStatements = accStatus.find()
    return render_template('account_statement.html',account_statement=True,accountStatements=accountStatements)
