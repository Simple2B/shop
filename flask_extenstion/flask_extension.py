from flask import Flask


class FlaskExtension:
    """Use this class as a virtual class for flask extenstions"""

    def __init__(self, app: Flask = None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Override this method"""
        raise NotImplementedError
