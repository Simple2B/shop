from datetime import datetime as dt


def datetime_outputfilter(v):
    return dt.strptime(v, "%Y-%m-%d %H:%M:%S") if v else None


def date_outputfilter(v):
    return dt.strptime(v, "%Y-%m-%d").date() if v else None
