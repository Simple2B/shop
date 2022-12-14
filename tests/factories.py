# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from flaskshop.database import db
from flaskshop.account.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Sequence(lambda n: "user{0}".format(n))
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = Sequence(lambda n: "user{0}".format(n))
    # password = PostGenerationMethodCall('set_password', 'example')
    is_active = True

    class Meta:
        """Factory configuration."""

        model = User
