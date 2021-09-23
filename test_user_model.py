"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

TEST_USER_DATA_1 = {
    "email":"test@test.com",
    "username":"testuser",
    "password":"HASHED_PASSWORD"
}

TEST_USER_DATA_2 = {
    "email":"test2@test.com",
    "username":"testuser2",
    "password":"HASHED_PASSWORD"
}

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        test_user_1 = User(**TEST_USER_DATA_1)
        test_user_2 = User(**TEST_USER_DATA_2)
        db.session.add_all([test_user_1, test_user_2])
        db.session.commit()

        self.test_user_1 = test_user_1
        self.test_user_2 = test_user_2

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User1 should have no messages & no followers
        self.assertEqual(len(self.test_user_1.messages), 0)
        self.assertEqual(len(self.test_user_1.followers), 0)

        # User2 should have no messages & no followers
        self.assertEqual(len(self.test_user_2.messages), 0)
        self.assertEqual(len(self.test_user_2.followers), 0)
