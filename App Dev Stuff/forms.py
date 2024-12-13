from wtforms import Form
from wtforms import BooleanField
from wtforms import StringField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import EmailField
from wtforms import DateField
from wtforms import TextAreaField
from wtforms import RadioField
from wtforms import validators

# from wtforms.widgets import HiddenInput
# import pycountry, us
# from flask import Flask, render_template

# from config import USER_ROLES as ROLES
# from config import EVENT_TYPES as E_TYPES
# from config import VOLUNTEER_TYPES as V_TYPES
# from config import GENDERS
# from datastructure import User as User

# USERNAMES = [user.fullname for user in User.query.all() if user.role == 'organizer']

# STATES = [s.name for s in us.STATES]

# COUNTRIES = [c.name for c in pycountry.countries]

# errors = {
#     'fname': "Please enter your first name.",
#     'lname': "Please enter your email address.",
#     'email': "Please enter your email address.",
#     'street': "Please enter your address.",
#     'state': "Please select your state.",
#     'country': "Please select your country."
# }   

# class BaseEditForm(Form):
#     def __call__(self, row):
#         for col in self._fields.keys():
#             attr = row.__getattribute__(col)
#             self[col].data = attr

#     def getSubmitText(self):
#         return "Confirm Changes"

# class SignUpForm(Form):
#     fname = StringField('First Name', [validators.InputRequired()])
#     lname = StringField('Last Name', [validators.InputRequired()])
#     gender = SelectField('Gender', [validators.InputRequired()], choices=GENDERS)
#     email = EmailField('Email', [validators.InputRequired(), validators.Email()], render_kw={'placeholder': 'yourname@example.com'})
#     address = StringField('Address', [validators.InputRequired()], render_kw={'placeholder': 'Enter your home address'})
#     is_idd = BooleanField('Are you I/DD?')
#     has_bkg_check = BooleanField('Have you completed a backgorund check (For Volunteers)')
#     open_to_check = BooleanField('If you haven\'t already completed a background check, are you open to it?')
#     has_volunteer_form = BooleanField('Have you completed a volunteer application form? (For Volunteers)')
    
#     def getHeaderText(self):
#          return "Sign Up"
    
#     def getSubmitText(self):
#          return "Sign up"

# # class AdminSignUpForm(SignUpForm):
#     # role = SelectField("Role", [validators.InputRequired()], choices=ROLES, default="default")

# #     def getHeaderText(self):
# #          return "Sign Up"
    
# #     def getSubmitText(self):
# #          return "Sign up"

# class LoginForm(Form):
#     uname = StringField('Username', [validators.InputRequired()], render_kw={'placeholder': 'Enter your username to login'})

#     def getHeaderText(self):
#          return "Log In"
    
#     def getSubmitText(self):
#          return "Login"

# class EditUserForm(BaseEditForm, SignUpForm):
#     def getHeaderText(self):
#         return "Edit User Profile"

# class EditUserAdminForm(AdminSignUpForm, BaseEditForm):
#     pass

# class CreateEventForm(Form):
#     event_name = StringField('Event Name', [validators.InputRequired()], render_kw={'placeholder': 'What is this event called?'})
#     date = DateField('Date', [validators.InputRequired()])
#     location = StringField('Location (Street Address)', [validators.InputRequired()], render_kw={'placeholder': 'Where is the event being held?'})
#     organizer_name = SelectField('Organizer', [validators.InputRequired()], choices=USERNAMES)
#     event_type = SelectField('Event Type', [validators.InputRequired()], choices=E_TYPES, render_kw={'class': 'small-select'})
#     volunteer_type = SelectField('Volunteering Type', [validators.InputRequired()], choices=V_TYPES)
#     description = TextAreaField('Description', [validators.Length(max=500)], render_kw={'placeholder': 'Desribe the event (optional)...'})

#     def __call__(self, organizer):
#         print(f"Default: {organizer}")
#         self.organizer_name.__setattr__ ('default', organizer) 
#         self.organizer_name.__setattr__ ('value', organizer) 

#     def getHeaderText(self):
#          return "Create A New Event"
    
#     def getSubmitText(self):
#          return "Create"

# class EditEventForm(BaseEditForm, CreateEventForm):
#     def getHeaderText(self):
#         return "Edit Event"
    

# class SelectTableForm(Form):
#     table = SelectField('Select Table to View', [validators.InputRequired()], choices=[('user', 'Users'), ('event', 'Events')])