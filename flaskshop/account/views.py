# -*- coding: utf-8 -*-
"""User views."""
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_required, current_user, login_user, logout_user
from pluggy import HookimplMarker
from flask_babel import lazy_gettext
import random
import string
from .forms import (
    AddressForm,
    LoginForm,
    RegisterForm,
    SetPasswordForm,
    ForgotPasswdForm,
)
from .models import UserAddress, User, gen_password_reset_id
from .utils import message_sender_for_set_password
from flaskshop.utils import flash_errors
from flaskshop.order.models import Order
from flaskshop.logger import log

impl = HookimplMarker("flaskshop")


@login_required
def index():
    form = SetPasswordForm(request.form)
    orders = Order.get_current_user_orders()

    if form.validate_on_submit():
        user = current_user
        user.password = form.password_confirmation.data
        user.save()
        flash(
            lazy_gettext("Update passport was successful"),
            "success",
        )
    if form.errors:
        log(log.WARNING, "form error: [%s]", form.errors)
        flash(
            lazy_gettext("Password does not match"),
            "danger",
        )

    return render_template("account/details.html", form=form, orders=orders)


def login():
    """login page."""
    form = LoginForm(request.form)
    if form.validate_on_submit():
        login_user(form.user)
        redirect_url = request.args.get("next") or url_for("public.home")
        flash(lazy_gettext("You are log in."), "success")
        return redirect(redirect_url)
    else:
        log(log.ERROR, "Invalid data [%s]", form.errors)
        flash_errors(form)
    return render_template("account/login.html", form=form)


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def resetpwd():
    """Reset user password"""
    form = ForgotPasswdForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.reset_password_uid = gen_password_reset_id()
        user.save()

        message_to_send = message_sender_for_set_password(
            user=user, html_dir="account/partials/email_forgot_passwd.html"
        )
        current_app.mail.send(message_to_send)

        flash(
            lazy_gettext(f"Confirmation email was sent to {form.email.data.lower()}"),
            "success",
        )
        return redirect(url_for("account.login"))
    else:
        log(log.ERROR, "Invalid data [%s]", form.errors)
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
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
        )
        user.save()

        message_to_send = message_sender_for_set_password(
            user=user, html_dir="account/partials/email_confirmation.html"
        )
        current_app.mail.send(message_to_send)

        flash(
            lazy_gettext(f"Confirmation email was sent to {form.email.data.lower()}"),
            "success",
        )
        return redirect(url_for("public.home"))
    else:
        log(log.ERROR, "Invalid data [%s]", form.errors)
        flash_errors(form)
    return render_template("account/signup.html", form=form)


def set_password(reset_password_uid: str):
    user: User = User.query.filter(
        User.reset_password_uid == reset_password_uid
    ).first()

    if not user:
        log(log.ERROR, "wrong reset_password_uid. [%s]", reset_password_uid)
        flash("Incorrect reset password link", "danger")
        return redirect(url_for("account.index"))

    form = SetPasswordForm(request.form)

    if form.validate_on_submit():
        user.password = form.password.data
        user.reset_password_uid = ""
        user.is_active = True
        user.save()
        login_user(user)
        flash("Login successful.", "success")
        return redirect(url_for("account.index"))
    elif form.is_submitted():
        log(log.WARNING, "form error: [%s]", form.errors)
        flash("Wrong user password.", "danger")
    return render_template(
        "account/password_reset.html", form=form, reset_password_uid=reset_password_uid
    )


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
        log(log.ERROR, "Invalid data [%s]", form.errors)
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
    bp.add_url_rule("/", view_func=index, methods=["GET", "POST"])
    bp.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    bp.add_url_rule("/resetpwd", view_func=resetpwd, methods=["GET", "POST"])
    bp.add_url_rule("/logout", view_func=logout)
    bp.add_url_rule("/signup", view_func=signup, methods=["GET", "POST"])
    bp.add_url_rule(
        "/setpwd/<reset_password_uid>", view_func=set_password, methods=["GET", "POST"]
    )
    bp.add_url_rule("/address", view_func=addresses)
    bp.add_url_rule("/address/edit", view_func=edit_address, methods=["GET", "POST"])
    bp.add_url_rule(
        "/address/<int:id>/delete", view_func=delete_address, methods=["POST"]
    )

    app.register_blueprint(bp, url_prefix="/account")
