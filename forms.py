"""WTForms form definitions for cafe submission and admin login."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, URL


class CafeForm(FlaskForm):
    name           = StringField("Cafe Name",            validators=[DataRequired(), Length(max=250)])
    location       = StringField("London Neighbourhood", validators=[DataRequired(), Length(max=250)])
    map_url        = URLField(  "Google Maps URL",       validators=[DataRequired(), URL()])
    img_url        = URLField(  "Photo URL",             validators=[DataRequired(), URL()])
    seats          = StringField("Seats",                validators=[Optional(), Length(max=250)])
    coffee_price   = StringField("Coffee Price",         validators=[Optional(), Length(max=250)])
    has_wifi       = BooleanField("Has WiFi")
    has_sockets    = BooleanField("Has Power Sockets")
    has_toilet     = BooleanField("Has Toilets")
    can_take_calls = BooleanField("Can Take Calls")
    submit         = SubmitField("Submit Cafe")


class AdminLoginForm(FlaskForm):
    username = StringField( "Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Log In")
