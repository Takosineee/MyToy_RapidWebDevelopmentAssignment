from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField
from wtforms.validators import InputRequired,email

# form used in basket
class CheckoutForm(FlaskForm):
    firstname = StringField("Your first name", validators=[InputRequired()])
    surname = StringField("Your surname", validators=[InputRequired()])
    phone = StringField("Your phone number", validators=[InputRequired()])
    email = StringField("Your email", validators=[InputRequired(), email()])
    address = StringField("Your address", validators=[InputRequired()])
    submit = SubmitField("Send")