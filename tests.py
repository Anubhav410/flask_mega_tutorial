import os
from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,  'test_db/app_test.db')

class UserModelCase(unittest.TestCase):
	def setUp(self):
		db.create_all()

	def tearDown(self):
		db.session.remove()
        db.drop_all()


	def test_password_hashing(self):
		user = User(username='Susan', email='susan@test.com')
		user.set_password('dog')

		self.assertFalse(user.check_password('cat'))
		self.assertTrue(user.check_password('dog'))
    	

	def test_avatar(self):
		user = User(username='john', email='john@example.com')
		self.assertEqual(user.avatar(128), ("https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128"))

	def test_follow(self):
		u1 = User(username='john', email="john@ex.com")
		u2 = User(username='susan', email="susan@ex.com")
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertEqual(u1.followed.all(), [])
		self.assertEqual(u2.followed.all(), [])

		u1.follow(u2)
		db.session.commit()
		self.assertTrue(u1.is_following(u2))

	def _test_follow(self):
		u1 = User(username='john1', email='john1@example.com')
		u2 = User(username='susan1', email='susan1@example.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertEqual(u1.followed.all(), [])
		self.assertEqual(u1.followers.all(), [])

		u1.follow(u2)
		db.session.commit()
		self.assertTrue(u1.is_following(u2))
		self.assertEqual(u1.followed.count(), 1)
		self.assertEqual(u1.followed.first().username, 'susan')
		self.assertEqual(u2.followers.count(), 1)
		self.assertEqual(u2.followers.first().username, 'john')

		u1.unfollow(u2)
		db.session.commit()
		self.assertFalse(u1.is_following(u2))
		self.assertEqual(u1.followed.count(), 0)
		self.assertEqual(u2.followers.count(), 0)


	def _test_follow_posts(self):
		# create four users
		u1 = User(username='john11', email='john11@example.com')
		u2 = User(username='susan11', email='susan11@example.com')
		u3 = User(username='mary11', email='mary11@example.com')
		u4 = User(username='david11', email='david11@example.com')
		db.session.add_all([u1, u2, u3, u4])

		 # create four posts
		now = datetime.utcnow()
		p1 = Post(body="post from john", author=u1,
		          timestamp=now + timedelta(seconds=1))
		p2 = Post(body="post from susan", author=u2,
		          timestamp=now + timedelta(seconds=4))
		p3 = Post(body="post from mary", author=u3,
		          timestamp=now + timedelta(seconds=3))
		p4 = Post(body="post from david", author=u4,
		          timestamp=now + timedelta(seconds=2))
		db.session.add_all([p1, p2, p3, p4])
		db.session.commit()

		 # setup the followers
		u1.follow(u2)  # john follows susan
		u1.follow(u4)  # john follows david
		u2.follow(u3)  # susan follows mary
		u3.follow(u4)  # mary follows david
		db.session.commit()

		# check the followed posts of each user
		f1 = u1.followed_posts().all()
		f2 = u2.followed_posts().all()
		f3 = u3.followed_posts().all()
		f4 = u4.followed_posts().all()
		self.assertEqual(f1, [p2, p4, p1])
		self.assertEqual(f2, [p2, p3])
		self.assertEqual(f3, [p3, p4])
		self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)