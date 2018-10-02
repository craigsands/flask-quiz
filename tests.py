import unittest
from flask_testing import TestCase

from app import create_app, db
from app.models import User


class TestDb(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return create_app(self)

    def setUp(self):
        db.create_all()

    def test_user(self):
        user = User(username='craigsands', pw_hash='testing')
        db.session.add(user)
        db.session.commit()

        # this works
        print('assert')
        assert user in db.session

        response = self.client.get('/')
        print(response)
        print('assert2')
        # this raises an AssertionError
        assert user in db.session

    def tearDown(self):
        db.session.remove()
        db.drop_all()


# class QuizCase(TestCase):
#     def setUp(self):
#         self.q = Quiz()
#         self.q.load_from_excel('instance/quiz/sample-quiz.xlsx')
#
#     def test_rows(self):
#         from pprint import pprint
#         pprint(self.q._datasets)
#
#     def test_questions(self):
#         self.q.build_questions()
#
#         from pprint import pprint
#         pprint(self.q.questions)


if __name__ == '__main__':
    unittest.main()