from datetime import datetime, timezone
from hashlib import md5
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login


followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)


class User(db.Model, UserMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))

    tpacks: so.WriteOnlyMapped['ActivityToPlan'] = so.relationship('Travelplan', back_populates='owner')
    """
        email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                                 unique=True)
    """

    """
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    """

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

"""
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return db.session.get(User, id)
        
    """


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

"""
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
"""

class Destination(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))

    activity_des: so.WriteOnlyMapped['Activities'] = so.relationship('Activities', back_populates='destination_activity')

    plan_des: so.WriteOnlyMapped['Travelplan'] = so.relationship('Travelplan', back_populates='destination_plan')


class Travelplan(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    time_needed: so.Mapped[str] = so.mapped_column(sa.String(140))
    budget: so.Mapped[int] = so.mapped_column()
    group_rec: so.Mapped[int] = so.mapped_column()

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

    destination_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('destination.id'))
    destination_activity: so.Mapped['Destination'] = so.relationship('Destination', back_populates='activity_des')

    activity_link: so.WriteOnlyMapped['ActivityToPlan'] = so.relationship('ActivityToPlan', back_populates="active")


class ActivityToPlan(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    plan_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('travelplan.id'))
    plan: so.Mapped['Travelplan'] = so.relationship('Travelplan', back_populates="plan_link")

    activity_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('activities.id'))
    active: so.Mapped['Activities'] = so.relationship('Activities', back_populates="activity_link")

""" 
class TravelPackage(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    WILL Have the plan and just general special things like rating and maybe the saved bit
"""
