# -*- coding: utf-8 -*-
"""User views."""
import os
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    session,
)
from flask_login import login_required, current_user, login_user, logout_user
from flaskshop.extensions import csrf_protect, login_manager
from flask_mail import Message
from pluggy import HookimplMarker
from flask_babel import lazy_gettext
import random
import string

from .forms import AddressForm, LoginForm, RegisterForm, ChangePasswordForm, ResetPasswd
from .models import OpenidProviders, UserAddress, User
from flaskshop.utils import flash_errors
from flaskshop.order.models import Order
from flaskshop.logger import log
import requests

impl = HookimplMarker("flaskshop")

# JS !!!!!
# how to add https
@csrf_protect.exempt
def google_auth():
    token = request.json["access_token"]
    if token:
        user_data = requests.get(
            f"https://openidconnect.googleapis.com/v1/userinfo?access_token={token}"
        )
        # if user_data:
        user_data = user_data.json()
        email_verified = user_data["email_verified"]
        if not email_verified:
            flash(lazy_gettext("Please,activate your Google Account"), "error")
            return redirect("account.index")
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            user = User.create(
                open_id=user_data["sub"],
                email=user_data["email"],
                is_active=True,
                username=user_data["email"],
                provider=OpenidProviders.GOOGLE,
            )
        login_user(user)
        log(log.INFO, f"User logged in.Profile:{user_data}")
    else:
        flash(lazy_gettext("Error while logging in via Google"), "error")
    return redirect(url_for("account.index"))


@csrf_protect.exempt
def facebook_auth():
    token = request.json["access_token"]
    user_id = request.json["user_id"]
    if token:
        user_data = requests.get(
            f"https://graph.facebook.com/{user_id}?fields=id,name,email,picture&access_token={token}"
        )
        user_data = user_data.json()
        user = User.query.filter_by(
            email=user_data["email"],
        ).first()
        if not user:
            user = User.create(
                open_id=user_data["id"],
                email=user_data["email"],
                is_active=True,
                username=user_data["email"],
                provider=OpenidProviders.FACEBOOK,
            )
        login_user(user)
        log(log.INFO, f"User logged in.Profile:{user_data}")
    else:
        flash(lazy_gettext("Error while logging in via Facebook"), "error")
    return redirect(url_for("account.index"))


def index():
    form = ChangePasswordForm(request.form)
    orders = Order.get_current_user_orders()
    return render_template("account/details.html", form=form, orders=orders)


def login():
    """login page."""
    if current_user.is_authenticated:
        return redirect(url_for("account.index"))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        login_user(form.user)
        redirect_url = request.args.get("next") or url_for("public.home")
        flash(lazy_gettext("You are log in."), "success")
        return redirect(redirect_url)
    else:
        flash_errors(form)

    return render_template(
        "account/login.html",
        form=form,
        google_api_key=current_app.config["GOOGLE_API_KEY"],
        google_client_id=current_app.config["GOOGLE_CLIENT_ID"],
        facebook_app_id=current_app.config["FACEBOOK_APP_ID"],
    )


@login_manager.unauthorized_handler
def unauthorized():
    return render_template("errors/401.html"), 401


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def resetpwd():

    """Reset user password"""
    form = ResetPasswd(request.form)

    if form.validate_on_submit():
        flash(lazy_gettext("Check your e-mail."), "success")
        user = User.query.filter_by(email=form.username.data).first()
        new_passwd = id_generator()
        body = render_template("account/reser_passwd_mail.html", new_passwd=new_passwd)
        msg = Message(lazy_gettext("Reset Password"), recipients=[form.username.data])
        msg.body = lazy_gettext(
            """We cannot simply send you your old password.\n
        A unique password has been generated for you. Change the password after logging in.\n
        New Password is: %s"""
            % new_passwd
        )
        msg.html = body
        mail = current_app.extensions.get("mail")
        mail.send(msg)
        user.update(password=new_passwd)
        return redirect(url_for("account.login"))
    else:
        flash_errors(form)
    return render_template("account/login.html", form=form, reset=True)


@login_required
def logout():
    """Logout."""
    logout_user()
    flash(lazy_gettext("You are logged out."), "info")
    return redirect(url_for("public.home"))


def signup():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User.create(
            username=form.username.data,
            email=form.email.data.lower(),
            password=form.password.data,
            is_active=True,
        )
        login_user(user)
        flash(lazy_gettext("You are signed up."), "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("account/signup.html", form=form)


def set_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        current_user.update(password=form.password.data)
        flash(lazy_gettext("You have changed password."), "success")
    else:
        flash_errors(form)
    return redirect(url_for("account.index"))


def addresses():
    """List addresses."""
    addresses = current_user.addresses
    return render_template("account/addresses.html", addresses=addresses)


def edit_address():
    """Create and edit an address."""
    form = AddressForm(request.form)
    address_id = request.args.get("id", None, type=int)
    if address_id:
        user_address = UserAddress.get_by_id(address_id)
        form = AddressForm(request.form, obj=user_address)
    if request.method == "POST" and form.validate_on_submit():
        address_data = {
            "province": form.province.data,
            "city": form.city.data,
            "district": form.district.data,
            "address": form.address.data,
            "contact_name": form.contact_name.data,
            "contact_phone": form.contact_phone.data,
            "user_id": current_user.id,
        }
        if address_id:
            UserAddress.update(user_address, **address_data)
            flash(lazy_gettext("Success edit address."), "success")
        else:
            UserAddress.create(**address_data)
            flash(lazy_gettext("Success add address."), "success")
        return redirect(url_for("account.index") + "#addresses")
    else:
        flash_errors(form)
    return render_template(
        "account/address_edit.html", form=form, address_id=address_id
    )


def delete_address(id):
    user_address = UserAddress.get_by_id(id)
    if user_address in current_user.addresses:
        UserAddress.delete(user_address)
    return redirect(url_for("account.index") + "#addresses")


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("account", __name__)
    google_bp = Blueprint("google", __name__)
    facebook_bp = Blueprint("facebook", __name__)

    google_bp.add_url_rule(
        "/auth",
        view_func=google_auth,
        methods=["POST"],
    )

    facebook_bp.add_url_rule("/auth/", view_func=facebook_auth, methods=["GET", "POST"])

    bp.add_url_rule("/", view_func=index, methods=["GET"])
    bp.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    bp.add_url_rule("/resetpwd", view_func=resetpwd, methods=["GET", "POST"])
    bp.add_url_rule("/logout", view_func=logout)
    bp.add_url_rule("/signup", view_func=signup, methods=["GET", "POST"])
    bp.add_url_rule("/setpwd", view_func=set_password, methods=["POST"])
    bp.add_url_rule("/address", view_func=addresses)
    bp.add_url_rule("/address/edit", view_func=edit_address, methods=["GET", "POST"])
    bp.add_url_rule(
        "/address/<int:id>/delete", view_func=delete_address, methods=["POST"]
    )

    app.register_blueprint(bp, url_prefix="/account")
    app.register_blueprint(google_bp, url_prefix="/google")
    app.register_blueprint(facebook_bp, url_prefix="/facebook")
