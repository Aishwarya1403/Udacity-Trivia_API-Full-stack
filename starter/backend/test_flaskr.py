import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res= self.client().get('/categories')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
    
    def test_get_questions(self):
        res= self.client().get('/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(len(data["questions"]))

    def test_deletion(self):
        res=self.client().delete('/questions/5')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_deletion(self):
        res=self.client().delete('/questions/1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    def test_post_questions(self):
        new_ques={
            'question':'xyz',
            'answer': 'abc',
            'difficulty':2,
            'category':2
        }
        res=self.client().post('/questions', json=new_ques)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.asserEqual(data["success"], True)

    def test_422_post_questions(self):
        new_ques={
            'question':'xyz',
            'answer': 'abc',
            'difficulty':2,
            'category':2
        }
        res=self.client().post('/questions', json=new_ques)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.asserEqual(data["success"], False)
        self.asserEqual(data["message"], 'Unprocessable Entity')

    
    def test_search_questions(self):
        search={
            'term':'Tom'
        }
        res= self.client().post('/search', json=search)
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)

    def test_422_on_search(self):
        search={
            'term':'10000'
        }
        res=self.client().post('search', json=search)
        data=json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEquall(data["success"], False)
        self.assertEqual(data["message"],'Unprocessable Request')

    def test_get_questionsByCategory(self):
        res=self.client().get('/categories/2/questions')
        data=json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertEqual(res.status_code, 200)

    def test_playing_quizzes(self):
        info={
            'previous_questions':[],
            'quiz_category':{
                'category':'History',
                'id':4
            }
        }
        res=self.client.post('/quizzes', json=info)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_400_in_quizzes(self):
        info={
            'previous_questions':[],
        }
        res.self.client.post('/quizzes', json=info)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.asserEqual(data["success"], False)
        self.assertEqual(data["message"], 'Bad Request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()