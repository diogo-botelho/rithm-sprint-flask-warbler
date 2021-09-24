"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask import session, g

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

TEST_USER_DATA_1 = {
    "email":"test@test.com",
    "username":"testuser",
    "password":"HASHED_PASSWORD",
    "image_url":""
}

TEST_USER_DATA_2 = {
    "email":"test2@test.com",
    "username":"testuser2",
    "password":"HASHED_PASSWORD",
    "image_url":""
}

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        test_user_1 = User.signup(**TEST_USER_DATA_1)
        test_user_2 = User.signup(**TEST_USER_DATA_2)
        db.session.add_all([test_user_1, test_user_2])
        db.session.commit()

        self.test_user_1_id = test_user_1.id
        self.test_user_2_id = test_user_2.id

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        test_user_1 = User.query.get(self.test_user_1_id)

        # User1 should have no messages & no followers
        self.assertEqual(len(test_user_1.messages), 0)
        self.assertEqual(len(test_user_1.followers), 0)
        self.assertEqual(User.query.count(),2)

    def test_repr_method(self):
        """Test that __repr__ works"""

        test_user_1 = User.query.get(self.test_user_1_id)        
        
        self.assertEqual(f"{test_user_1}",f"<User #{test_user_1.id}: {test_user_1.username}, {test_user_1.email}>")

    def test_login_works(self):
        """Test if login works."""

        url = '/login'
        resp = self.client.post(url,json = {"username": "test_user", "password": "HASHED_PASSWORD"},follow_redirects=True)

        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        breakpoint()
        self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
        # self.assertEqual(session[CURR_USER_KEY],self.test_user_1_id)


    def test_is_following(self):
        """Test user1 is following user2"""

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.test_user_1_id

        url = f"/users/follow/{self.test_user_2_id}"
        resp = self.client.post(url,follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('<p>@testuser2</p>',html)
        self.assertEqual(Follows.query.count(), 1)


    # def test_is_not_following()
