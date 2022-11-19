class Fake:
    # a fake class to hook when not use redis but clear mc need rdb
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        pass

    def delete(self, *args, **kwargs):
        pass

    def __iter__(self):
        yield 1
