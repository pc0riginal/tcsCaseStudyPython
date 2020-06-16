from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField,PasswordField,SubmitField,SelectField,IntegerField
from wtforms.validators import DataRequired,Required,NumberRange,Regexp,Length,ValidationError

class LoginForm(FlaskForm):
    username = StringField(label="Username",validators=[DataRequired()])
    password = PasswordField(label="Password",validators=[DataRequired()])
    submit = SubmitField(label="Login")

accounts = [('Saving','saving'),('Current','current')]
class CreateAccount(FlaskForm):
    customerID = StringField(label="Customer ID(SSN ID)",validators=[DataRequired(),Regexp('^\\d{9}$',message="required 9 digit ID")])
    account_type = SelectField(label="Account Type",choices=accounts,validators=[Required()])
    amount = IntegerField(label="Amount",validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField(label="Create")

class DeleteAccount(FlaskForm):
    customerID = StringField(label="Customer ID",validators=[DataRequired()])
    account_type = SelectField(label="Account Type",choices=accounts,validators=[Required()])
    submit = SubmitField(label="Delete")

class CreateCustomer(FlaskForm):
    customerID = StringField(label="Customer ID(SSN ID)",validators=[DataRequired(),Regexp('^\\d{9}$',message="required 9 digit ID")])
    name = StringField(label="Name",validators=[DataRequired(),Length(min=3)])
    age = IntegerField(label="Age",validators=[DataRequired(),NumberRange(min=10,max=100)])
    addressline1 = StringField('Address Line 1*',validators=[DataRequired(), Length(min=1, max=100)])
    addressline2 = StringField('Address Line 2',validators=[Length(max=100)])
    city = StringField('City',validators=[DataRequired()])
    state = StringField('State',validators=[DataRequired()])
    submit = SubmitField(label="Create")

class UpdateCustomer(FlaskForm):
    customerID = StringField(label="Customer ID(SSN ID)",validators=[DataRequired(),Regexp('^\\d{9}$',message="required 9 digit ID")])
    submit = SubmitField(label="Update")
    
