"""User views tests."""

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

class UserViewsTestCase(TestCase):
    """Test views for users."""

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


##############################################################################
# User signup/login/logout

    def test_valid_signup(self):
        """Test user sign-up route worksv with valid credentials"""

        url='/signup'
        resp = self.client.post(url,json = {"username": "testuser_3", "email": "test3@test.com", "password": "HASHED_PASSWORD"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('id="home-aside"', html)
        self.assertIn('<p>@testuser_3</p>', html)


    def test_invalid_signup(self):
        """Test user sign-up route worksv with valid credentials"""

        url='/signup'
        resp = self.client.post(url,json = {"username": None, "email": "test3@test.com", "password": "HASHED_PASSWORD"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('Join Warbler today.', html)


    # def test_valid_authenticate(self):
    #     """Test user authentication works with valid credentials."""

    #     url = '/login'
    #     resp = self.client.post(url,json = {"username": "testuser", "password": "HASHED_PASSWORD"},follow_redirects=True)
    #     html = resp.get_data(as_text=True)

    #     self.assertEqual(resp.status_code,200)
    #     self.assertIn('Hello, testuser!', html)


    # def test_invalid_username_authenticate(self):
    #     """Test user authentication does not work with invalid username."""

    #     url = '/login'
    #     resp = self.client.post(url,json = {"username": "i_am_invalid", "password": "HASHED_PASSWORD"},follow_redirects=True)
    #     html = resp.get_data(as_text=True)

    #     self.assertEqual(resp.status_code,200)
    #     # breakpoint()
    #     self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
    #     self.assertIn('Invalid credentials', html)

    #     # TO FIX: Csrf token is not being passed into post request


    def test_logout(self):
        """Test logout works."""

        with self.client.session_transaction() as session:
            session[CURR_USER_KEY] = self.test_user_1_id

        url = '/logout'
        resp = self.client.post(url,follow_redirects=True)
        html = resp.get_data(as_text=True)
 
        self.assertEqual(resp.status_code,200)
        self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
        # self.assertNotEqual(sess[CURR_USER_KEY],self.test_user_1_id)

##############################################################################
# General user routes:

    def test_list_all_users(self):
        """Test showing list of users"""

        url = '/users'
        resp = self.client.get(url)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('id="user-index-list"', html)

 
    def test_finds_user(self):
        """Test showing user found."""

        url = '/users?q=testuser'
        resp = self.client.get(url)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('id="user-index-list"', html)
        self.assertIn('<p>@testuser</p>', html)

    def test_finds_no_user(self):
        """Test showing no user found."""

        url = '/users?q=testuser4'
        resp = self.client.get(url)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('Sorry, no users found', html)     

    def test_users_show_successful(self):
        """Test showing user details."""

        url = f'/users/{self.test_user_1_id}'
        resp = self.client.get(url)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('id="user-show-details"', html)

    def test_users_show_unsuccessful(self):
        """Test showing user details."""

        url = f'/users/0'
        resp = self.client.get(url)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,404)






    # def test_is_following(self):
    #     """Test user1 is following user2"""

    #     with self.client.session_transaction() as sess:
    #         sess[CURR_USER_KEY] = self.test_user_1_id

    #     url = f"/users/follow/{self.test_user_2_id}"
    #     resp = self.client.post(url,follow_redirects=True)
    #     # html = resp.get_data(as_text=True)
    #     test_user_1 = User.query.get(self.test_user_1_id)
    #     test_user_2 = User.query.get(self.test_user_2_id)

    #     # self.assertEqual(resp.status_code,200)
    #     # self.assertIn('<p>@testuser2</p>',html)
    #     self.assertEqual(Follows.query.count(), 1)
    #     self.assertTrue(test_user_1.is_following(test_user_2))


    # def test_is_not_following(self):
    #     """Test user1 is NOT following user2"""

    #     with self.client.session_transaction() as sess:
    #         sess[CURR_USER_KEY] = self.test_user_1_id

    #     test_user_1 = User.query.get(self.test_user_1_id)
    #     test_user_2 = User.query.get(self.test_user_2_id)

    #     self.assertEqual(Follows.query.count(), 0)
    #     self.assertFalse(test_user_1.is_following(test_user_2))


    # def test_is_followed_by(self):
    #     """Test user2 is followed by user1"""

    #     with self.client.session_transaction() as sess:
    #         sess[CURR_USER_KEY] = self.test_user_1_id

    #     url = f"/users/follow/{self.test_user_2_id}"
    #     resp = self.client.post(url,follow_redirects=True)
    #     # html = resp.get_data(as_text=True)
    #     test_user_1 = User.query.get(self.test_user_1_id)
    #     test_user_2 = User.query.get(self.test_user_2_id)

    #     # self.assertEqual(resp.status_code,200)
    #     # self.assertIn('<p>@testuser2</p>',html)
    #     self.assertEqual(Follows.query.count(), 1)
    #     self.assertTrue(test_user_2.is_followed_by(test_user_1))


    # def test_is_not_followed_by(self):
    #     """Test user2 is NOT followed by user1"""

    #     with self.client.session_transaction() as sess:
    #         sess[CURR_USER_KEY] = self.test_user_1_id

    #     test_user_1 = User.query.get(self.test_user_1_id)
    #     test_user_2 = User.query.get(self.test_user_2_id)

    #     self.assertEqual(Follows.query.count(), 0)
    #     self.assertFalse(test_user_2.is_followed_by(test_user_1)