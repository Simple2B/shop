# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_babel import lazy_gettext

from .models import User


class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(5, 30)],
        render_kw={"placeholder": "Enter your username..."},
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email..."},
    )

    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError("This username is taken.")

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError("This email is already registered.")


class ForgotPasswdForm(FlaskForm):

    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email..."},
    )

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError("Email is not found")


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        lazy_gettext("Username Or Email"),
        validators=[DataRequired(message="with username")],
        render_kw={"placeholder": "Enter your username..."},
    )
    password = PasswordField(
        lazy_gettext("Password"),
        validators=[DataRequired(message="with password")],
        render_kw={"placeholder": "Enter your password..."},
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


class SetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(6, 30)],
        render_kw={"placeholder": "Set your new password..."},
    )
    password_confirmation = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Password do not match."),
        ],
        render_kw={"placeholder": "Repeat your password..."},
    )
    submit = SubmitField("Save")

    def validate(self):
        """Validate the form."""
        initial_validation = super().validate()
        if not initial_validation:
            return False

        return True


class AddressForm(FlaskForm):
    """Address form."""

    province = StringField(
        lazy_gettext("Province"),
        validators=[DataRequired()],
        render_kw={"placeholder": "Set your province..."},
    )
    city = StringField(
        lazy_gettext("City"),
        validators=[DataRequired()],
        render_kw={"placeholder": "Set your city..."},
    )
    district = StringField(
        lazy_gettext("District"),
        validators=[DataRequired()],
        render_kw={"placeholder": "Set your district..."},
    )
    address = StringField(
        lazy_gettext("Address"),
        validators=[DataRequired()],
        render_kw={"placeholder": "Set your address..."},
    )
    contact_name = StringField(
        lazy_gettext("Contact name"),
        validators=[DataRequired()],
        render_kw={"placeholder": "Set your contact name..."},
    )
    contact_phone = StringField(
        lazy_gettext("Contact Phone"),
        validators=[DataRequired(), Length(min=10, max=13)],
        render_kw={"placeholder": "Set your phone number..."},
    )
    # shipping_methods = IntegerField(lazy_gettext("Shipping Methods"),)

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super().__init__(*args, **kwargs)
        self
