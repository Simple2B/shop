import copy
from .date_filter import date_outputfilter, datetime_outputfilter


class PropsItem:
    def __init__(self, name, default=None, output_filter=None, pre_set=None):
        self.name = name
        self.default = default
        self.output_filter = output_filter
        self.pre_set = pre_set

    def __get__(self, obj, objtype):
        r = obj.get_props_item(self.name, None)
        if r is None:
            return copy.deepcopy(self.default)
        elif self.output_filter:
            return self.output_filter(r)
        else:
            return r

    def __set__(self, obj, value):
        if self.pre_set:
            value = self.pre_set(value)
        obj.set_props_item(self.name, value)

    def __delete__(self, obj):
        obj.delete_props_item(self.name)


# TODO could be removed?
class DatetimePropsItem(PropsItem):
    def __init__(self, name, default=None):
        super().__init__(name, default, datetime_outputfilter)


class DatePropsItem(PropsItem):
    def __init__(self, name, default=None):
        super().__init__(name, default, date_outputfilter)
