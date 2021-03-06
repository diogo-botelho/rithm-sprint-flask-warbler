"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    DEFAULT_IMG_URL = "/static/images/default-pic.png"
    DEFAULT_HEADER_IMG_URL = "/static/images/warbler-hero.jpg"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default=DEFAULT_IMG_URL,
    )

    header_image_url = db.Column(
        db.Text,
        default=DEFAULT_HEADER_IMG_URL
    )

    bio = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    location = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message', 
        order_by='Message.timestamp.desc()',
        backref='user')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    liked_messages = db.relationship(
        'Message',
        secondary="likes",
        # cascade="all,delete",
        backref="user_likes",
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    # def set_of_liked_messages(self):
    #     """ Returns a set of liked messages by the user """

    #     return set(self.liked_messages)

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?
        Takes in user instance as argument, returns True/False."""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?
        Takes in user instance as argument, returns True/False."""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1
    
    def add_or_remove_like(self, message):
        """ Takes in a message. If the user has already liked the message, will remove
        the like from the message. If the user has not already liked the message, will
        add the like to the message. 
        """

        if self in message.user_likes:
            message.user_likes.remove(self)
        else:          
            message.user_likes.append(self)

    
    @classmethod
    def hash_password(cls,password):
        """Encrypt a password using bcrypt"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        return hashed_pwd


    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """
        # hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        hashed_pwd = User.hash_password(password)

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

class Like(db.Model):
    """ An individual user like for a message """

    __tablename__ = 'likes'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='CASCADE'),
        primary_key=True,
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)