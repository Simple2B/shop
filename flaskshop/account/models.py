from operator import or_
from functools import reduce
from uuid import uuid4
from libgravatar import Gravatar

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property


from flaskshop.database import Column, Model, db
from flaskshop.extensions import bcrypt
from flaskshop.constant import Permission


def gen_password_reset_id() -> str:
    return str(uuid4())


class User(Model, UserMixin):

    __tablename__ = "account_user"
    username = Column(db.String(64), unique=True, nullable=False, comment="user`s name")
    email = Column(db.String(64), unique=True, nullable=False)
    #: The hashed password
    _password = db.Column(db.String(128), nullable=True, default=None)
    nick_name = Column(db.String(64))
    is_active = Column(db.Boolean, default=False)
    open_id = Column(db.String(64), index=True)
    session_key = Column(db.String(128), index=True)
    reset_password_uid = db.Column(db.String(64), default=gen_password_reset_id)

    def __str__(self):
        return self.username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.generate_password_hash(value).decode("UTF-8")

    @property
    def avatar(self):
        return Gravatar(self.email).get_image()

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password.encode("utf-8"), value)

    @property
    def addresses(self):
        return UserAddress.query.filter_by(user_id=self.id).all()

    @property
    def is_active_human(self):
        return "Y" if self.is_active else "N"

    @property
    def roles(self):
        at_ids = (
            UserRole.query.with_entities(UserRole.role_id)
            .filter_by(user_id=self.id)
            .all()
        )
        return Role.query.filter(Role.id.in_(id for id, in at_ids)).all()

    def delete(self):
        for addr in self.addresses:
            addr.delete()
        return super().delete()

    def can(self, permissions):
        if not self.roles:
            return False
        all_perms = reduce(or_, map(lambda x: x.permissions, self.roles))
        return all_perms >= permissions

    def can_admin(self):
        return self.can(Permission.ADMINISTER)

    def can_edit(self):
        return self.can(Permission.EDITOR)

    def can_op(self):
        return self.can(Permission.OPERATOR)


class UserAddress(Model):
    __tablename__ = "account_address"
    user_id = Column(db.Integer)
    province = Column(db.String(256))
    city = Column(db.String(256))
    district = Column(db.String(256))
    address = Column(db.String(256))
    contact_name = Column(db.String(256))
    contact_phone = Column(db.String(64))

    @property
    def full_address(self):
        return (
            f"{self.province}<br>{self.city}<br>{self.district}"
            f"<br>{self.address}<br>{self.contact_name}<br>{self.contact_phone}"
        )

    @hybrid_property
    def user(self):
        return User.get_by_id(self.user_id)

    def __str__(self):
        return self.full_address


class Role(Model):
    __tablename__ = "account_role"
    name = Column(db.String(64), unique=True)
    permissions = Column(db.Integer(), default=Permission.LOGIN)


class UserRole(Model):
    __tablename__ = "account_user_role"
    user_id = Column(db.Integer())
    role_id = Column(db.Integer())
