from datetime import datetime, timezone
from hashlib import md5
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login

saved_packages = db.Table(
    'saved_packages',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('travelplan_id', db.Integer, db.ForeignKey('travelplan.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))

    tpacks: so.WriteOnlyMapped['ActivityToPlan'] = so.relationship('Travelplan', back_populates='owner')

    saved_travelplans = db.relationship(
        'Travelplan',
        secondary=saved_packages,
        backref=db.backref('saved_by_users', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Destination(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))

    activity_des: so.WriteOnlyMapped['Activities'] = so.relationship('Activities', back_populates='destination_activity')
    plan_des: so.WriteOnlyMapped['Travelplan'] = so.relationship('Travelplan', back_populates='destination_plan')


class Travelplan(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    time_needed: so.Mapped[int] = so.mapped_column()
    budget: so.Mapped[int] = so.mapped_column()
    group_rec: so.Mapped[int] = so.mapped_column()
    image_filename = db.Column(db.String(200))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    owner: so.Mapped['User'] = so.relationship('User', back_populates='tpacks')

    destination_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('destination.id'))
    destination_plan: so.Mapped['Destination'] = so.relationship('Destination', back_populates='plan_des')

    plan_link: so.WriteOnlyMapped['ActivityToPlan'] = so.relationship('ActivityToPlan', back_populates='plan')


class Activities(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    establishment: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[str] = so.mapped_column(sa.String(140))
    image_filename = db.Column(db.String(200))

    destination_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('destination.id'))
    destination_activity: so.Mapped['Destination'] = so.relationship('Destination', back_populates='activity_des')

    activity_link: so.WriteOnlyMapped['ActivityToPlan'] = so.relationship('ActivityToPlan', back_populates="active")


class ActivityToPlan(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    plan_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('travelplan.id'))
    plan: so.Mapped['Travelplan'] = so.relationship('Travelplan', back_populates="plan_link")

    activity_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('activities.id'))
    active: so.Mapped['Activities'] = so.relationship('Activities', back_populates="activity_link")
