import time
from datetime import datetime
import json

from flask_babel import lazy_gettext
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    current_app,
    url_for,
    abort,
    Response,
)
from flask_login import login_required, current_user
from pluggy import HookimplMarker
import stripe

from .models import Order, OrderPayment, OrderLine
from flaskshop.extensions import csrf_protect
from flaskshop.constant import ShipStatusKinds, PaymentStatusKinds, OrderStatusKinds

impl = HookimplMarker("flaskshop")


@login_required
def index():
    return redirect(url_for("account.index"))


@login_required
def show(token):
    order = Order.query.filter_by(token=token).first()
    if not order.is_self_order:
        abort(403, lazy_gettext("This is not your order!"))
    return render_template(
        "orders/details.html",
        order=order,
        stripe_publishable_key=current_app.config["STRIPE_PUBLISHABLE_KEY"],
    )


def create_payment(token, payment_method):
    order = Order.query.filter_by(token=token).first()
    if order.status != OrderStatusKinds.unfulfilled.value:
        abort(403, lazy_gettext("This Order Can Not Pay"))
    payment_no = str(int(time.time())) + str(current_user.id)
    customer_ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    payment = OrderPayment.query.filter_by(order_id=order.id).first()
    if payment:
        payment.update(
            payment_no=payment_no,
            payment_method=payment_method,
            customer_ip_address=customer_ip_address,
            status=PaymentStatusKinds.waiting.value,
        )
    else:
        payment = OrderPayment.create(
            order_id=order.id,
            payment_method=payment_method,
            payment_no=payment_no,
            total=order.total,
            customer_ip_address=customer_ip_address,
            status=PaymentStatusKinds.waiting.value,
        )
    return payment


@csrf_protect.exempt
def stripe_pay():
    order = Order.query.filter_by(token=request.json["token"]).first()
    orderline = OrderLine.query.filter_by(order_id=order.id)

    create_payment(order.token, "stripe")

    product_names = []

    for line in orderline:
        product_names.append(line.product_name)

    if not order:
        return abort(404)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=current_user.email,
        payment_intent_data={
            "metadata": {"order_token": f"{order.token}"},
            "receipt_email": current_user.email,
        },
        line_items=[
            {
                "name": ",".join(map(str, product_names)),
                # "images": ["https://example.com/t-shirt.png"],
                "amount": int(order.total * 100),
                "currency": "usd",
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=current_app.config["BASE_WEBSITE_URL"]
        + url_for("order.payment_success"),
        cancel_url=current_app.config["BASE_WEBSITE_URL"]
        + url_for("order.payment_error"),
    )
    return {"session": session}


@csrf_protect.exempt
def stripe_payment_webhook():
    event = None
    payload = request.data
    payload_json = json.loads(payload)

    order_token = payload_json["data"]["object"]["metadata"].get("order_token")
    if order_token:
        order = Order.query.filter_by(token=order_token).first()

        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except ValueError:
            return Response(status=400)

        if event.type == "payment_intent.succeeded":
            order.update(
                status=OrderStatusKinds.fulfilled.value,
            )
            order.payment.update(
                status=PaymentStatusKinds.confirmed.value,
            )

        if (
            event.type == "payment_intent.canceled"
            and event.type == "payment_intent.payment_failed"
        ):
            order.update(
                status=OrderStatusKinds.unfulfilled.value,
            )
            order.payment.update(
                status=PaymentStatusKinds.rejected.value,
            )
    return Response(status=200)


# for test pay flow
@login_required
def test_pay(token):
    payment = create_payment(token, "testpay")
    payment.pay_success(paid_at=datetime.now())
    return redirect(url_for("order.payment_success"))


@login_required
def payment_success():
    return render_template("orders/checkout_success.html")


@login_required
def payment_error():
    return render_template("orders/checkout_error.html")


@login_required
def cancel_order(token):
    order = Order.query.filter_by(token=token).first()
    if not order.is_self_order:
        abort(403, "This is not your order!")
    order.cancel()
    return render_template("orders/details.html", order=order)


@login_required
def receive(token):
    order = Order.query.filter_by(token=token).first()
    order.update(
        status=OrderStatusKinds.completed.value,
        ship_status=ShipStatusKinds.received.value,
    )
    return render_template("orders/details.html", order=order)


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("order", __name__)
    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/<string:token>", view_func=show)
    # bp.add_url_rule("/pay/<string:token>/alipay", view_func=ali_pay)
    bp.add_url_rule("/pay/stripe", view_func=stripe_pay, methods=["POST"])
    bp.add_url_rule(
        "/pay/stripe/webhook", view_func=stripe_payment_webhook, methods=["POST"]
    )
    # bp.add_url_rule("/alipay/notify", view_func=ali_notify, methods=["POST"])
    bp.add_url_rule("/pay/<string:token>/testpay", view_func=test_pay)

    bp.add_url_rule("/payment/success", view_func=payment_success)
    bp.add_url_rule("/payment/error", view_func=payment_error)

    bp.add_url_rule("/cancel/<string:token>", view_func=cancel_order)
    bp.add_url_rule("/receive/<string:token>", view_func=receive)

    app.register_blueprint(bp, url_prefix="/orders")
