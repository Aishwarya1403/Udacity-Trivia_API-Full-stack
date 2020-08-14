import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors=CORS(app, resources={r"/api/*":{"origins":"*"}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  QUESTIONS_PER_PAGE = 10
  def paginate(request, selection):
    page=request.args.get('page',1,type=int)
    start=(page-1) * QUESTIONS_PER_PAGE
    end=start+ QUESTIONS_PER_PAGE
    cur_ques = selection[start:end]

    return cur_ques 

  @app.route('/categories')
  def get_categories():
    try:    
      categories = Category.query.all()
      formatted = {category.id: category.type for category in categories}
      result={
        "success":True,
        "count": 2,
        "categories": formatted 
      }
      return jsonify(result)
    except Exception:
      abort(500)
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    all_ques=Question.query.all()
    type_ques=[question.format() for question in all_ques]

    total=len(type_ques)
    cur_ques=paginate(request,type_ques)
    all_cate=Category.query.all()
    type_cate={category.id: category.type for category in all_cate}
    result={
      "success":True,
      "questions":cur_ques,
      "total_questions":total,
      "categories":type_cate
      
    }
    return jsonify(result),200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def del_by_id(id):
    try:
      question_id=Question.query.filter(Question.id==id).one_or_none()
      if question_id is None:
        abort(404)
      
      question_id.delete()
      
      result={
        "success":True,
        "id":id
      }
      return jsonify(result)

    except Exception:
      abort(422)


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def new_question():
    
    body= request.get_json()
    ques= body.get('question')
    ans= body.get('answer')
    category = body.get('category')
    difficulty= body.get('difficulty')

    try:
      add_ques=Question(question=ques, answer=ans, category=category, difficulty=difficulty)
      add_ques.insert()
      result={
        "success":True,
        "message":"successfully added a question"
      }
      return jsonify(result),200

    except Exception:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def search_ques():
    body = request.get_json()
    search_term = body.get('searchTerm', '')
    #if search_term in body: 
    result = Question.question.ilike('%{}%'.format(search_term))      
    filtered = Question.query.filter(result)
    search = [question.format() for question in filtered]
    print(len(search))
    if (len(search)== 0):
      abort(422)
    else:
      result={
        "success": True,
        "questions": search,
        "totalQuestions": len(search)
        }
      return jsonify(result), 200
    


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def category_questions(id):
    categorize= Category.query.filter_by(id=id).all()
    questions= Question.query.filter_by(category=id).all()
    formatted_ques=[question.format() for question in questions]
    result={
      "success":True,
      "questions":formatted_ques
    }

    return jsonify(result),200

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/play', methods=['POST'])
  def start_quiz():
    try:
      data = request.get_json()
      print(data)
      category_id = data['quiz_category']['id']
      category = Category.query.get(category_id)
      previous_questions = data["previous_questions"]

      if not (category_id =='0'):
        if "previous_questions" in data and len(previous_questions) > 0:
          print(data)
          questions = Question.query.filter(Question.id.notin_(previous_questions), Question.category == category.id).all()
        else:
          print(data)
          questions = Question.query.filter(Question.category == category.id).all()
      else: 
        print(data)
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        print(len(questions))
      
      max = len(questions)
      if max == 0:
        question = None
      else:
        question = questions[random.randrange(0,max)].format()

      return jsonify({
        "success": True,
        "question": question
      }),200

    except:
      abort(500, "An error occured while trying to load the next question")

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'message':'Requested entity is Not Found',
      'error':404
    }),404

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'message': 'Unprocessable Entity',
      'error' : 422
    }),422

  @app.errorhandler(400)
  def bad_req(error):
    return jsonify({
      'success': False,
      'message':'Bad Request',
      'error': 400
    }), 400

  @app.errorhandler(500)
  def internal_err(error):
    return jsonify({
      'success':False,
      'message':'Internal Server Error',
      'error':500
    }), 500
  
  return app

    
