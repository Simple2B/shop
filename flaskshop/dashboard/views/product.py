from datetime import datetime
import random

from flask import request, render_template, redirect, url_for, current_app, flash
from flask_login import login_required
from flask_babel import lazy_gettext, gettext

from flaskshop.extensions import csrf_protect
from flaskshop.product.models import (
    ProductAttribute,
    Collection,
    Product,
    Category,
    ProductType,
    ProductVariant,
    ProductImage,
)
from flaskshop.dashboard.forms import (
    AttributeForm,
    CollectionForm,
    CategoryForm,
    ProductTypeForm,
    ProductForm,
    ProductCreateForm,
    VariantForm,
)


def generate_product_id():
    import uuid

    id_string = str(uuid.uuid4().int)
    product_id = int(id_string[0:8])
    return product_id


def attributes():
    page = request.args.get("page", type=int, default=1)
    query = ProductAttribute.query

    title = request.args.get("title", type=str)
    if title:
        query = query.filter(ProductAttribute.title.ilike(f"%{title}%"))
    pagination = query.paginate(page, current_app.config["PAGINATION_ITEMS_PER_PAGE"])
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "values_label": lazy_gettext("Value"),
        "types_label": lazy_gettext("ProductType"),
    }
    context = {
        "title": lazy_gettext("Product Attribute"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": gettext("attributes"),
    }
    return render_template("list.html", **context)


def attributes_manage(id=None):
    if id:
        attr = ProductAttribute.get_by_id(id)
        form = AttributeForm(obj=attr)
    else:
        form = AttributeForm()
    if form.validate_on_submit():
        if not id:
            attr = ProductAttribute()
        attr.id = int(random.randint(1, 100000))
        attr.title = form.title.data
        attr.update_types(form.types.data)
        attr.update_values(form.values.data)
        attr.save()
        return redirect(url_for("dashboard.attributes"))
    product_types = ProductType.query.all()
    return render_template(
        "product/attribute.html", form=form, product_types=product_types
    )


def collections():
    page = request.args.get("page", type=int, default=1)
    query = Collection.query
    title = request.args.get("title", type=str)
    if title:
        query = query = query.filter(Collection.title.ilike(f"%{title}%"))
    pagination = query.paginate(page, current_app.config["PAGINATION_ITEMS_PER_PAGE"])
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "title": lazy_gettext("Product Collection"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": gettext("collections"),
    }
    return render_template("list.html", **context)


def collections_manage(id=None):
    if id:
        collection = Collection.get_by_id(id)
        form = CollectionForm(obj=collection)
    else:
        form = CollectionForm()
    if form.validate_on_submit():
        if not id:
            collection = Collection()
        collection.title = form.title.data
        collection.update_products(form.products.data)
        image = form.bgimg_file.data
        if image:
            background_img = image.filename
            upload_file = current_app.config["UPLOAD_DIR"] / background_img
            upload_file.write_bytes(image.read())
            collection.background_img = (
                current_app.config["UPLOAD_FOLDER"] + "/" + background_img
            )
        collection.save()
        return redirect(url_for("dashboard.collections"))
    products = Product.query.all()
    return render_template("product/collection.html", form=form, products=products)


def categories():
    page = request.args.get("page", type=int, default=1)
    query = Category.query

    title = request.args.get("title", type=str)
    if title:
        query = query.filter(Category.title.ilike(f"%{title}%"))

    pagination = query.paginate(page, current_app.config["PAGINATION_ITEMS_PER_PAGE"])

    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "parent": lazy_gettext("Parent"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "title": lazy_gettext("Product Category"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": gettext("categories"),
    }
    return render_template("list.html", **context)


def categories_manage(id=None):
    if id:
        category = Category.get_by_id(id)
        form = CategoryForm(obj=category)
    else:
        form = CategoryForm()
    if form.validate_on_submit():
        if not id:
            category = Category()
        category.title = form.title.data
        category.parent_id = form.parent_id.data
        image = form.bgimg_file.data
        if image:
            background_img = image.filename
            upload_file = current_app.config["UPLOAD_DIR"] / background_img
            upload_file.write_bytes(image.read())
            category.background_img = (
                current_app.config["UPLOAD_FOLDER"] + "/" + background_img
            )
        category.save()
        return redirect(url_for("dashboard.categories"))
    parents = Category.first_level_items()
    return render_template("product/category.html", form=form, parents=parents)


def product_types():
    page = request.args.get("page", type=int, default=1)
    query = ProductType.query
    title = request.args.get("title", type=str)
    if title:
        query = query.filter(ProductType.title.ilike(f"%{title}%"))
    pagination = query.paginate(page, current_app.config["PAGINATION_ITEMS_PER_PAGE"])
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "has_variants": lazy_gettext("Has Variants"),
        "is_shipping_required": lazy_gettext("Is Shipping Required"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "title": lazy_gettext("Product Type"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": gettext("product_types"),
    }
    return render_template("list.html", **context)


def product_types_manage(id=None):
    if id:
        product_type = ProductType.get_by_id(id)
        form = ProductTypeForm(obj=product_type)
    else:
        form = ProductTypeForm()
    if form.validate_on_submit():
        if not id:
            product_type = ProductType()
        product_type.update_product_attr(form.product_attributes.data)
        product_type.update_variant_attr(form.variant_attr_id.data)
        del form.product_attributes
        del form.variant_attr_id
        form.populate_obj(product_type)
        product_type.save()
        return redirect(url_for("dashboard.product_types"))
    attributes = ProductAttribute.query.all()
    return render_template(
        "product/product_type.html", form=form, attributes=attributes
    )


def products():
    page = request.args.get("page", type=int, default=1)
    query = Product.query

    on_sale = request.args.get("sale", type=bool)
    if on_sale:
        query = query.filter_by(on_sale=on_sale)
    category = request.args.get("category", type=int)
    if category:
        query = query.filter_by(category_id=category)
    title = request.args.get("title", type=str)
    if title:
        query = query.filter(Product.title.ilike(f"%{title}%"))
    created_at = request.args.get("created_at", type=str)
    if created_at:
        start_date, end_date = created_at.split("-")
        start_date = datetime.strptime(start_date.strip(), "%m/%d/%Y")
        end_date = datetime.strptime(end_date.strip(), "%m/%d/%Y")
        query = query.filter(Product.created_at.between(start_date, end_date))

    pagination = query.paginate(page, current_app.config["PAGINATION_ITEMS_PER_PAGE"])
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "on_sale_human": lazy_gettext("On Sale"),
        "sold_count": lazy_gettext("Sold Count"),
        "price_human": lazy_gettext("Price"),
        "category": lazy_gettext("Category"),
    }
    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "categories": Category.query.all(),
    }
    return render_template("product/list.html", **context)


def product_detail(id):
    product = Product.get_by_id(id)
    return render_template("product/detail.html", product=product)


def _save_product(product, form):
    product.update_images(form.images.data)
    product.update_attributes(form.attributes.data)
    del form.images
    del form.attributes
    form.populate_obj(product)
    product.save()
    return product


def product_edit(id):
    product = Product.get_by_id(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        _save_product(product, form)
        return redirect(url_for("dashboard.product_detail", id=product.id))
    categories = Category.query.all()
    context = {"form": form, "categories": categories, "product": product}
    return render_template("product/product_edit.html", **context)


def product_create_step1():
    form = ProductCreateForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                "dashboard.product_create_step2",
                product_type_id=form.product_type_id.data,
            )
        )
    product_types = ProductType.query.all()
    return render_template(
        "product/product_create_step1.html", form=form, product_types=product_types
    )


def product_create_step2():
    form = ProductForm()
    product_type_id = request.args.get("product_type_id", 1, int)
    product_type = ProductType.get_by_id(product_type_id)
    categories = Category.query.all()
    if form.validate_on_submit():
        category_id = int(request.form["category_id"])
        if category_id == 0:
            flash("Please, pick a category for your product", "danger")
            return render_template(
                "product/product_create_step2.html",
                form=form,
                product_type=product_type,
                categories=categories,
            )
        product = Product(id=generate_product_id(), product_type_id=product_type_id)
        product = _save_product(product, form)
        # product.generate_variants()
        return redirect(url_for("dashboard.product_detail", id=product.id))
    return render_template(
        "product/product_create_step2.html",
        form=form,
        product_type=product_type,
        categories=categories,
    )


def variant_manage(id=None):
    if id:
        variant = ProductVariant.get_by_id(id)
        form = VariantForm(obj=variant)
    else:
        form = VariantForm()
    if form.validate_on_submit():
        if not id:
            variant = ProductVariant()
        form.populate_obj(variant)
        product_id = request.args.get("product_id")
        if product_id:
            variant.product_id = product_id
        variant.sku = str(variant.product_id) + "-" + str(form.sku_id.data)
        variant.save()
        return redirect(url_for("dashboard.product_detail", id=variant.product_id))
    return render_template("product/variant.html", form=form)


@login_required
@csrf_protect.exempt
def dashboard_product_delete_image():
    if request.method == "DELETE":
        img_id = request.json["imgId"]
        ProductImage.get_by_id(img_id).delete()
        return dict(), 200
    return {"error": "error"}, 400
