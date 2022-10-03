from flask import request
from flask_login import login_required

from flaskshop.extensions import csrf_protect
from flaskshop.account.models import User
from flaskshop.product.models import (
    ProductType,
    Category,
    Collection,
    ProductAttribute,
    Product,
    ProductVariant,
    ProductImage,
)
from flaskshop.discount.models import Sale, Voucher
from flaskshop.dashboard.models import DashboardMenu
from flaskshop.public.models import Page, MenuItem
from .utils import ApiResult, wrap_partial


def item_del(cls, id):
    try:
        item = cls.get_by_id(id)
        item.delete()
    except Exception as e:
        print(e)
        return ApiResult({"msg": str(e)})
    return ApiResult(dict())


user_del = wrap_partial(item_del, User)
product_del = wrap_partial(item_del, Product)
variant_del = wrap_partial(item_del, ProductVariant)
collection_del = wrap_partial(item_del, Collection)
category_del = wrap_partial(item_del, Category)
sale_del = wrap_partial(item_del, Sale)
voucher_del = wrap_partial(item_del, Voucher)
attribute_del = wrap_partial(item_del, ProductAttribute)
product_type_del = wrap_partial(item_del, ProductType)
dashboard_menu_del = wrap_partial(item_del, DashboardMenu)
site_page_del = wrap_partial(item_del, Page)
site_menu_del = wrap_partial(item_del, MenuItem)


@login_required
@csrf_protect.exempt
def dashboard_product_delete_image():
    if request.method == "DELETE":
        ProductImage.get_by_id()
        return dict(), 200
    return {"error": "error"}, 400
