from elasticsearch_dsl import Boolean, Document, Integer, Float, Date, Text
from elasticsearch.helpers import parallel_bulk
from flask_sqlalchemy import Pagination
from elasticsearch_dsl.connections import connections

# from flaskshop.settings import Config


SEARCH_FIELDS = ["title^10", "description^5"]

# WE NEED TO CREATE INDEX !!!


def get_item_data(item):
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "first_img": item.first_img,
        "basic_price": item.basic_price,
        "price": item.price,
        "on_sale": item.on_sale,
        "is_discounted": item.is_discounted,
    }


class Item(Document):
    id = Integer()
    title = Text()
    description = Text()
    first_img = Text()
    basic_price = Float()
    price = Float()
    on_sale = Boolean()
    is_discounted = Boolean()
    created_at = Date()

    class Index:
        name = "flaskshop"

    @classmethod
    def add(cls, item):
        obj = cls(meta={"id": item.id}, **get_item_data(item))
        obj.save()
        return obj

    @classmethod
    def update_item(cls, item):
        obj = cls.get(item.id)

        kw = get_item_data(item)
        obj.update(**kw)
        return True

    @classmethod
    def delete(cls, item):
        rs = cls.get(item.id)
        if rs:
            super(cls, rs).delete()
            return True
        return False

    @classmethod
    def bulk_update(cls, items, chunk_size=5000, op_type="update", **kwargs):
        index = cls._index._name
        _type = cls._doc_type.name
        obj = [
            {
                "_op_type": op_type,
                "_id": f"{doc.id}",
                "_index": index,
                "_type": _type,
                "_source": get_item_data(doc),
            }
            for doc in items
        ]
        client = cls.get_es()
        rs = list(parallel_bulk(client, obj, chunk_size=chunk_size, **kwargs))
        return rs

    @classmethod
    def get_es(cls):
        search = cls.search()
        return connections.get_connection(search._using)

    @classmethod
    def new_search(cls, query, page, order_by=None, per_page=16):
        s = cls.search()
        s = s.query("multi_match", query=query, fields=SEARCH_FIELDS)
        start = (page - 1) * per_page
        s = s.extra(**{"from": start, "size": per_page})
        s = s if order_by is None else s.sort(order_by)
        rs = s.execute()
        items_total = rs.hits.total["value"]
        return Pagination(query, page, per_page, items_total, rs)
