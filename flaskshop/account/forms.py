# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from flask_babel import lazy_gettext

from .models import User


class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField("Username", validators=[DataRequired(), Length(2, 30)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])

    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError("This username is taken.")

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError("This email is already registered.")


class ResetPasswd(FlaskForm):
    """Password reset"""

    old_password = StringField(
        lazy_gettext("Enter your old password"), validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super().__init__(*args, **kwargs)
        self.user = current_user

    def validate_old_password(self, field):

        if not self.user.check_password(field.data):
            raise ValidationError("Invalid old password")


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        lazy_gettext("Username Or Email"),
        validators=[DataRequired(message="with username")],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        validators=[DataRequired(message="with password")],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super().validate()
        if not initial_validation:
            return False

        if "@" in self.username.data:
            self.user = User.query.filter_by(email=self.username.data).first()
        else:
            self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors += (lazy_gettext("Unknown username"),)
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors += (lazy_gettext("Invalid password"),)
            return False

        if not self.user.is_active:
            self.username.errors += (lazy_gettext("User not activated"),)
            return False

        return True


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(6, 30)])
    password_confirmation = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Password do not match."),
        ],
    )
    submit = SubmitField("Save")

    # def __init__(self, *args, **kwargs):
    #     """Create instance."""
    #     super().__init__(*args, **kwargs)
    #     self.user = current_user

    # def validate(self):
    #     """Validate the form."""
    #     initial_validation = super().validate()
    #     if not initial_validation:
    #         return False

    #     if not self.user.check_password(self.old_password.data):
    #         self.old_password.errors.append(lazy_gettext("Invalid password"))
    #         return False

    #     return True


class AddressForm(FlaskForm):
    """Address form."""

    province = StringField(lazy_gettext("Province"), validators=[DataRequired()])
    city = StringField(lazy_gettext("City"), validators=[DataRequired()])
    district = StringField(lazy_gettext("District"), validators=[DataRequired()])
    address = StringField(lazy_gettext("Address"), validators=[DataRequired()])
    contact_name = StringField(
        lazy_gettext("Contact name"), validators=[DataRequired()]
    )
    contact_phone = StringField(
        lazy_gettext("Contact Phone"),
        validators=[DataRequired(), Length(min=10, max=13)],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super().__init__(*args, **kwargs)
