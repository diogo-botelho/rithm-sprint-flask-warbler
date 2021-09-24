"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY
app.config['WTF_CSRF_ENABLED'] = False

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

TEST_USER_DATA_3 = {
    "email":"test3@test.com",
    "username":"testuser3",
    "password":"HASHED_PASSWORD",
    "image_url": None
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


    def test_is_following(self):
        """Test user1 is following user2"""

        test_user_1 = User.query.get(self.test_user_1_id)
        test_user_2 = User.query.get(self.test_user_2_id)

        test_user_2.followers.append(test_user_1)

        self.assertEqual(Follows.query.count(), 1)
        self.assertTrue(test_user_1.is_following(test_user_2))


    def test_is_not_following(self):
        """Test user1 is NOT following user2"""

        test_user_1 = User.query.get(self.test_user_1_id)
        test_user_2 = User.query.get(self.test_user_2_id)

        self.assertEqual(Follows.query.count(), 0)
        self.assertFalse(test_user_1.is_following(test_user_2))


    def test_is_followed_by(self):
        """Test user2 is followed by user1"""

        test_user_1 = User.query.get(self.test_user_1_id)
        test_user_2 = User.query.get(self.test_user_2_id)

        test_user_2.followers.append(test_user_1)

        self.assertEqual(Follows.query.count(), 1)
        self.assertTrue(test_user_2.is_followed_by(test_user_1))


    def test_is_not_followed_by(self):
        """Test user2 is NOT followed by user1"""

        test_user_1 = User.query.get(self.test_user_1_id)
        test_user_2 = User.query.get(self.test_user_2_id)

        self.assertEqual(Follows.query.count(), 0)
        self.assertFalse(test_user_2.is_followed_by(test_user_1))

    
    def test_valid_authenticate(self):
        """Test user authentication works with valid credentials."""

        test_user_1 = User.query.get(self.test_user_1_id)
        
        self.assertEqual(User.authenticate("testuser","HASHED_PASSWORD"),test_user_1)


    def test_invalid_username_authenticate(self):
        """Test user authentication does not work with invalid username."""

        test_user_1 = User.query.get(self.test_user_1_id)
        
        self.assertNotEqual(User.authenticate("random_user","HASHED_PASSWORD"),test_user_1)


    def test_invalid_password_authenticate(self):
        """Test user authentication does not work with invalid username."""

        test_user_1 = User.query.get(self.test_user_1_id)
        
        self.assertNotEqual(User.authenticate("testuser","RANDOM_PASSWORD"),test_user_1)


    def test_valid_signup(self):
        """Test user signup works with valid credentials."""

        test_user_3 = User.signup(**TEST_USER_DATA_3)
        db.session.commit()

        self.assertIsInstance(test_user_3,User)
        self.assertEqual(test_user_3.username,"testuser3")
        self.assertEqual(test_user_3.email,"test3@test.com")
        self.assertNotEqual(test_user_3.password,"HASHED_PASSWORD")
        self.assertTrue(test_user_3.password.startswith("$2b$12$"))
        self.assertEqual(test_user_3.image_url,"/static/images/default-pic.png")


    def test_none_username_signup(self):
        """Test user authentication does not work with invalid username."""

        User.signup(None, "anotheremail@test.com", "HASHED_PASSWORD", None)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

        self.assertIn('null value in column "username"', str(context.exception))


    def test_none_email_signup(self):
        """Test user authentication does not work with invalid email."""

        User.signup("test100", None, "HASHED_PASSWORD", None)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

        self.assertIn('null value in column "email"', str(context.exception))
    

    def test_none_password_signup(self):
        """Test user authentication does not work with invalid password."""
     
        with self.assertRaises(ValueError) as context:
            User.signup("test100", "anotheremail@test.com", None, None)
        
        self.assertIn('Password must be non-empty', str(context.exception))  


    def test_nonunique_username_signup(self):
        """Test user authentication does not work with non-unique username."""

        User.signup("testuser", "anotheremail@test.com", "HASHED_PASSWORD", None)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()
        
        self.assertIn('duplicate key value violates unique constraint "users_username_key"', str(context.exception))


    def test_nonunique_email_signup(self):
        """Test user authentication does not work with non-unique username."""

        User.signup("testuseragain", "test@test.com", "HASHED_PASSWORD", None)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()
        
        self.assertIn('duplicate key value violates unique constraint "users_email_key"', str(context.exception))