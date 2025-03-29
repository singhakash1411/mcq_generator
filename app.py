from flask import Flask, render_template, request, make_response, jsonify, url_for
from flask_bootstrap import Bootstrap
import spacy
from collections import Counter
import random
import PyPDF2
from PyPDF2 import PdfReader
from datetime import datetime
import json
from dotenv import load_dotenv
import os
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates',
    static_url_path='/static'
)
Bootstrap(app)

# Set Flask secret key
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Load spaCy model
try:
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")
    print("Successfully loaded spaCy model!")
except Exception as e:
    print(f"Error loading spaCy model: {e}")
    print("Please run: python -m spacy download en_core_web_sm")
    nlp = None

# In-memory storage for quizzes and responses
generated_quizzes = {}
quiz_responses = {}
used_questions = set()  # Track which questions have been used

# Programming-related questions database
PROGRAMMING_QUESTIONS = {
    'easy': [
        {
            'question': 'What is the output of print(2 + 2) in Python?',
            'options': ['3', '4', '5', '6'],
            'correct_answer': 'B'
        },
        {
            'question': 'Which of the following is a valid Python variable name?',
            'options': ['1variable', '_variable', 'class', 'for'],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the correct way to create a list in Python?',
            'options': ['list = []', 'list = {}', 'list = ()', 'list = <>'],
            'correct_answer': 'A'
        },
        {
            'question': 'What is the result of 5 % 2 in Python?',
            'options': ['2', '2.5', '1', '0'],
            'correct_answer': 'C'
        },
        {
            'question': 'Which operator is used for exponentiation in Python?',
            'options': ['^', '**', '^^', 'exp'],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the output of len("Hello")?',
            'options': ['4', '5', '6', '7'],
            'correct_answer': 'B'
        },
        {
            'question': 'Which method is used to convert a string to lowercase in Python?',
            'options': ['lower()', 'toLowerCase()', 'lowercase()', 'convertToLower()'],
            'correct_answer': 'A'
        },
        {
            'question': 'What is the output of print("Hello" * 2)?',
            'options': ['HelloHello', 'Hello 2', 'Error', 'HelloHelloHello'],
            'correct_answer': 'A'
        },
        {
            'question': 'Which of these is NOT a Python data type?',
            'options': ['int', 'float', 'char', 'str'],
            'correct_answer': 'C'
        },
        {
            'question': 'What is the output of print(3 * "Hi")?',
            'options': ['HiHiHi', '3Hi', 'Error', 'Hi 3'],
            'correct_answer': 'A'
        },
        {
            'question': 'Which method is used to add an element to a list?',
            'options': ['add()', 'append()', 'insert()', 'Both B and C'],
            'correct_answer': 'D'
        },
        {
            'question': 'What is the output of print(True and False)?',
            'options': ['True', 'False', 'Error', 'None'],
            'correct_answer': 'B'
        },
        {
            'question': 'Which of these is a valid way to create a tuple?',
            'options': ['tuple = ()', 'tuple = []', 'tuple = {}', 'tuple = <>'],
            'correct_answer': 'A'
        },
        {
            'question': 'What is the output of print(10 / 3)?',
            'options': ['3', '3.33', '3.3333333333333335', 'Error'],
            'correct_answer': 'C'
        },
        {
            'question': 'Which method is used to remove whitespace from both ends of a string?',
            'options': ['trim()', 'strip()', 'clean()', 'remove()'],
            'correct_answer': 'B'
        }
    ],
    'medium': [
        {
            'question': 'What is the difference between a list and a tuple in Python?',
            'options': [
                'Lists are immutable, tuples are mutable',
                'Lists are mutable, tuples are immutable',
                'There is no difference',
                'Lists can only contain numbers, tuples can contain any type'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the purpose of the __init__ method in Python classes?',
            'options': [
                'To destroy the object',
                'To initialize the object',
                'To create a new class',
                'To delete the class'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is a decorator in Python?',
            'options': [
                'A way to delete functions',
                'A way to modify functions or classes',
                'A way to create new variables',
                'A way to import modules'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between == and is in Python?',
            'options': [
                'There is no difference',
                '== compares values, is compares object identity',
                '== compares object identity, is compares values',
                'Both compare object identity'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is a lambda function in Python?',
            'options': [
                'A way to create loops',
                'An anonymous function',
                'A way to import modules',
                'A way to create classes'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the purpose of the yield keyword in Python?',
            'options': [
                'To stop program execution',
                'To create a generator function',
                'To define a class',
                'To import modules'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between append() and extend() in Python lists?',
            'options': [
                'There is no difference',
                'append adds a single element, extend adds multiple elements',
                'extend adds a single element, append adds multiple elements',
                'Both add multiple elements'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the purpose of the pass statement in Python?',
            'options': [
                'To stop program execution',
                'To create a placeholder',
                'To define a function',
                'To import modules'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between a method and a function in Python?',
            'options': [
                'There is no difference',
                'Methods are part of a class, functions are standalone',
                'Functions are part of a class, methods are standalone',
                'Both are part of a class'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the purpose of the super() function in Python?',
            'options': [
                'To create a superclass',
                'To call a parent class method',
                'To create a subclass',
                'To import modules'
            ],
            'correct_answer': 'B'
        }
    ],
    'hard': [
        {
            'question': 'What is a metaclass in Python?',
            'options': [
                'A way to create variables',
                'A way to create functions',
                'A way to create classes',
                'A way to delete classes'
            ],
            'correct_answer': 'C'
        },
        {
            'question': 'What is the Global Interpreter Lock (GIL) in Python?',
            'options': [
                'A way to lock files',
                'A mutex that protects access to Python objects',
                'A way to create global variables',
                'A way to delete global variables'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between __str__ and __repr__ in Python?',
            'options': [
                'There is no difference',
                '__str__ is for debugging, __repr__ is for display',
                '__str__ is for display, __repr__ is for debugging',
                'Both are for debugging'
            ],
            'correct_answer': 'C'
        },
        {
            'question': 'What is the purpose of the @property decorator in Python?',
            'options': [
                'To create a property',
                'To define a method as a property',
                'To create a class',
                'To import modules'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between a shallow copy and a deep copy in Python?',
            'options': [
                'There is no difference',
                'Shallow copy creates a new object, deep copy creates a reference',
                'Deep copy creates a new object, shallow copy creates a reference',
                'Both create references'
            ],
            'correct_answer': 'C'
        },
        {
            'question': 'What is the purpose of the __slots__ attribute in Python classes?',
            'options': [
                'To define class methods',
                'To restrict instance attributes',
                'To create class attributes',
                'To import modules'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between a class method and a static method in Python?',
            'options': [
                'There is no difference',
                'Class methods receive cls, static methods receive nothing',
                'Static methods receive cls, class methods receive nothing',
                'Both receive cls'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the purpose of the __call__ method in Python?',
            'options': [
                'To create a class',
                'To make an instance callable',
                'To define a method',
                'To import modules'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the difference between a generator and an iterator in Python?',
            'options': [
                'There is no difference',
                'Generators are functions, iterators are classes',
                'Iterators are functions, generators are classes',
                'Both are classes'
            ],
            'correct_answer': 'B'
        },
        {
            'question': 'What is the purpose of the __enter__ and __exit__ methods in Python?',
            'options': [
                'To create a class',
                'To implement context managers',
                'To define methods',
                'To import modules'
            ],
            'correct_answer': 'B'
        }
    ]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            if 'files[]' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file uploaded'
                }), 400

            files = request.files.getlist('files[]')
            if not files or files[0].filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400

            # Process all files and combine text
            combined_text = ""
            for file in files:
                if file and allowed_file(file.filename):
                    try:
                        if file.filename.endswith('.pdf'):
                            text = process_pdf(file)
                        else:  # txt file
                            text = file.read().decode('utf-8')
                        combined_text += text + "\n"
                    except Exception as e:
                        print(f"Error processing file {file.filename}: {e}")
                        continue

            if not combined_text.strip():
                return jsonify({
                    'success': False,
                    'error': 'No valid text content found in the uploaded files'
                }), 400

            # Generate MCQs from the combined text
            num_questions = int(request.form.get('num_questions', 5))
            try:
                mcqs = generate_mcqs(combined_text, num_questions)
                if not mcqs:
                    return jsonify({
                        'success': False,
                        'error': 'Could not generate questions from the provided text'
                    }), 400

                # Store quiz in memory
                quiz_id = None
                if not generated_quizzes:
                    quiz_id = '1'  # Assuming a single quiz for simplicity
                    generated_quizzes[quiz_id] = mcqs

                return jsonify({
                    'success': True,
                    'quiz_id': quiz_id,
                    'mcqs': mcqs
                })
            except Exception as e:
                print(f"Error generating MCQs: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Error generating questions: {str(e)}'
                }), 500

        return render_template('updated.html')
    except Exception as e:
        print(f"Error in index route: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        return f"Error: {str(e)}", 500

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('ds.html')

@app.route('/updated.html', methods=['GET'])
def updated():
    return render_template('updated.html')

def process_pdf(file):
    try:
        text = ""
        pdf_reader = PdfReader(file)
        if len(pdf_reader.pages) == 0:
            raise Exception("PDF file is empty")
            
        for page_num in range(len(pdf_reader.pages)):
            try:
                page_text = pdf_reader.pages[page_num].extract_text()
                if page_text.strip():
                    text += page_text + "\n"
            except Exception as e:
                print(f"Error extracting text from page {page_num + 1}: {e}")
                continue
                
        if not text.strip():
            raise Exception("No text content found in the PDF")
            
        return text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise Exception(f"Failed to process PDF file: {str(e)}")

def generate_mcqs(text, num_questions=5):
    if text is None or not text.strip():
        return []

    try:
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        if not sentences:
            raise Exception("No valid sentences found in the text")
            
        # Ensure we have enough sentences
        if len(sentences) < num_questions:
            # If we don't have enough sentences, we'll use what we have
            num_questions = len(sentences)
            print(f"Warning: Only {num_questions} sentences available in the text")
        
        selected_sentences = random.sample(sentences, num_questions)
        print(f"Generating {num_questions} questions from {len(sentences)} sentences")

        mcqs = []
        for sentence in selected_sentences:
            try:
                sent_doc = nlp(sentence)
                nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]
                verbs = [token.text for token in sent_doc if token.pos_ == "VERB"]
                named_entities = [ent.text for ent in sent_doc.ents]

                possible_answers = nouns + verbs + named_entities
                if not possible_answers:
                    continue

                question_word = random.choice(possible_answers)
                question_stem = sentence.replace(question_word, "______", 1)

                answer_choices = [question_word]
                distractors = list(set(possible_answers) - {question_word})

                # Generate more distractors if needed
                while len(distractors) < 3:
                    # Create a new distractor by modifying the question word
                    new_distractor = f"Modified_{question_word}_{len(distractors)}"
                    distractors.append(new_distractor)

                random.shuffle(distractors)
                for distractor in distractors[:3]:
                    answer_choices.append(distractor)

                random.shuffle(answer_choices)
                correct_answer = chr(64 + answer_choices.index(question_word) + 1)
                mcqs.append((question_stem, answer_choices, correct_answer))
            except Exception as e:
                print(f"Error generating MCQ for sentence: {sentence}")
                print(f"Error: {e}")
                continue

        if not mcqs:
            raise Exception("Could not generate any valid questions from the text")

        print(f"Successfully generated {len(mcqs)} questions")
        return mcqs
    except Exception as e:
        print(f"Error in generate_mcqs: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        raise Exception(f"Failed to generate questions: {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'txt'}

@app.route('/api/submit-response', methods=['POST'])
def submit_response():
    try:
        response_data = request.json
        if not response_data:
            return jsonify({
                'success': False,
                'error': 'No response data provided'
            }), 400

        # Validate required fields
        if 'responses' not in response_data:
            return jsonify({
                'success': False,
                'error': 'Responses are required'
            }), 400

        # Get questions from the request or memory
        questions = None
        if 'questions' in response_data:
            questions = response_data['questions']
        elif generated_quizzes:
            questions = generated_quizzes['1']

        # Calculate score based on questions
        score = 0
        total = len(response_data['responses'])
        
        if questions:
            for i, response in enumerate(response_data['responses']):
                if i < len(questions):
                    question = questions[i]
                    try:
                        # Handle both tuple format (PDF-generated) and dict format (API-generated)
                        if isinstance(question, tuple):
                            correct_answer = question[2]
                        else:
                            correct_answer = question.get('correct_answer')
                        
                        if response == correct_answer:
                            score += 1
                    except Exception as e:
                        print(f"Error processing question {i}: {e}")
                        continue

        return jsonify({
            'success': True,
            'score': score,
            'total': total
        })

    except Exception as e:
        print(f"Error in submit_response: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-quiz', methods=['POST'])
def generate_api_quiz():
    try:
        print("Received quiz generation request")
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        print(f"Request data: {data}")
        
        topic = data.get('topic', '').lower()
        difficulty = data.get('difficulty', 'easy')
        num_questions = int(data.get('num_questions', 5))

        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400

        print(f"Generating quiz for topic: {topic}, difficulty: {difficulty}, num_questions: {num_questions}")

        if topic == 'programming':
            # Get all available questions for the requested difficulty
            available_questions = [q for q in PROGRAMMING_QUESTIONS.get(difficulty, []) 
                                if q['question'] not in used_questions]
            
            # If we don't have enough questions for the requested difficulty,
            # get questions from other difficulties
            if len(available_questions) < num_questions:
                for diff in ['easy', 'medium', 'hard']:
                    if diff != difficulty:
                        additional_questions = [q for q in PROGRAMMING_QUESTIONS.get(diff, [])
                                             if q['question'] not in used_questions]
                        available_questions.extend(additional_questions)
            
            # If we still don't have enough questions, reset the used questions set
            if len(available_questions) < num_questions:
                print("Resetting used questions set as we've used all questions")
                used_questions.clear()
                available_questions = [q for q in PROGRAMMING_QUESTIONS.get(difficulty, [])]
                for diff in ['easy', 'medium', 'hard']:
                    if diff != difficulty:
                        available_questions.extend(PROGRAMMING_QUESTIONS.get(diff, []))

            # Randomly select questions
            selected_questions = random.sample(available_questions, min(num_questions, len(available_questions)))
            
            # Mark selected questions as used
            for q in selected_questions:
                used_questions.add(q['question'])
                print(f"Marked question as used: {q['question']}")

            print(f"Selected {len(selected_questions)} questions")
            print(f"Total questions used so far: {len(used_questions)}")

            # Store quiz in memory
            quiz_id = str(len(generated_quizzes) + 1)  # Generate unique quiz ID
            generated_quizzes[quiz_id] = selected_questions

            return jsonify({
                'success': True,
                'quiz_id': quiz_id,
                'questions': selected_questions
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Topic not supported yet'
            }), 400

    except Exception as e:
        print(f"Error in generate_api_quiz: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('subject', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400

        print(f"Received search query: {query}")
        
        # Generate questions based on the search query
        num_questions = int(request.args.get('num_questions', 5))
        print(f"Generating {num_questions} questions for query: {query}")
        
        # Check if the query matches any predefined topics
        query_lower = query.lower()
        if query_lower in ['programming', 'science', 'mathematics', 'history', 'geography', 'literature', 'technology', 'general knowledge']:
            # Use predefined questions for known topics
            if query_lower == 'programming':
                questions = PROGRAMMING_QUESTIONS.get('easy', [])
                if len(questions) < num_questions:
                    all_questions = []
                    for diff in ['easy', 'medium', 'hard']:
                        all_questions.extend(PROGRAMMING_QUESTIONS.get(diff, []))
                    questions = random.sample(all_questions, min(num_questions, len(all_questions)))
                else:
                    questions = random.sample(questions, min(num_questions, len(questions)))
                
                mcqs = questions
            else:
                # For other topics, generate questions from the query text
                mcqs = generate_mcqs(query, num_questions=num_questions)
        else:
            # For unknown topics, generate questions from the query text
            mcqs = generate_mcqs(query, num_questions=num_questions)
        
        if not mcqs:
            return jsonify({
                'success': False,
                'error': 'No questions found for the given search query'
            }), 404

        print(f"Generated {len(mcqs)} questions")

        # Store the quiz in memory
        quiz_id = '1'  # Assuming a single quiz for simplicity
        generated_quizzes['1'] = mcqs

        return jsonify({
            'success': True,
            'quiz_id': quiz_id,
            'mcqs': mcqs
        })

    except Exception as e:
        print(f"Error in search route: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\nStarting Flask application...")
    print("spaCy model status:", "Loaded" if nlp else "Not loaded")
    print("Access the application at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
