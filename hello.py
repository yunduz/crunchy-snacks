import sqlite3

from flask import Flask
from flask import g
from flask import jsonify


DATABASE = '/home/yunduz/development/repos/crunchy-snacks/db/pof_db'
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    db.row_factory = sqlite3.Row

    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    # import pdb; pdb.set_trace()
    cur.close()

    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/create/bingo_card/<int:user_id>')
def create_bingo_card(user_id):
    # create bingo card
    cur = get_db().execute('insert into bingocard (user_id) values (?);', [user_id])
    bingo_card_id = cur.lastrowid
    get_db().commit()

    bingo_card_info = {
        'bingo_card': {'id': bingo_card_id, 'complete': 0},
        'bingo_squares': []
    }

    # get questions randomly for the bingocard
    questions_sample_query = 'SELECT * FROM question ORDER BY RANDOM() LIMIT 9;'
    
    # import pdb; pdb.set_trace()
    # for each question create bingo square
    for idx, q in enumerate(query_db(questions_sample_query)):
        cur = get_db().execute('insert into bingosquare (bingo_card_id, question_id, idx) values (?, ?, ?);', [bingo_card_id, q['id'], idx])
        bingo_card_info['bingo_squares'].append(
            {
                'id': cur.lastrowid, 
                'question': {'id': q['id'], 'description': q['description']},
                'idx': idx
            }
        )

    get_db().commit()

    # return 'Created bingo card ' + str(bingo_card_id)
    return jsonify(bingo_card_info)

@app.route('/get/bingo_cards/complete/<int:user_id>')
def get_complete_bingo_cards(user_id):
    complete_bingo_cards = []

    bingo_cards_query = 'SELECT * FROM BingoCard WHERE user_id = ? AND complete = 1;'
    for bingo_card in query_db(bingo_cards_query, [user_id]):
        bingo_card_id = bingo_card['id']

        bingo_card_info = {
            'bingo_card': {'id': bingo_card_id, 'complete': 1},
            'bingo_squares': []
        }

        bingo_squares_query = 'SELECT BingoSquare.id as id, question.id as q_id, question.description as q_description, BingoSquare.idx as idx FROM BingoSquare JOIN question ON BingoSquare.question_id = question.id WHERE bingo_card_id = ?'
        for bingo_square in query_db(bingo_squares_query, bingo_card_id):
            bingo_card_info['bingo_squares'].append(
                {
                    'id': bingo_square['id'], 
                    'question': {'id': bingo_square['q_id'], 'description': bingo_square['q_description']},
                    'idx': bingo_square['idx']
                }
            )

        complete_bingo_cards.append(bingo_card_info)

    return jsonify(complete_bingo_cards)

@app.route('/get/bingo_cards/current/<int:user_id>')
def get_current_bingo_cards(user_id):
    complete_bingo_cards = []

    bingo_cards_query = 'SELECT * FROM BingoCard WHERE user_id = ? AND complete = 0;'
    for bingo_card in query_db(bingo_cards_query, [user_id]):
        bingo_card_id = bingo_card['id']

        bingo_card_info = {
            'bingo_card': {'id': bingo_card_id, 'complete': 0},
            'bingo_squares': []
        }

        bingo_squares_query = 'SELECT BingoSquare.id as id, question.id as q_id, question.description as q_description, BingoSquare.idx as idx FROM BingoSquare JOIN question ON BingoSquare.question_id = question.id WHERE bingo_card_id = ?'
        for bingo_square in query_db(bingo_squares_query, [bingo_card_id]):
            bingo_card_info['bingo_squares'].append(
                {
                    'id': bingo_square['id'], 
                    'question': {'id': bingo_square['q_id'], 'description': bingo_square['q_description']},
                    'idx': bingo_square['idx']
                }
            )

        complete_bingo_cards.append(bingo_card_info)

    return jsonify(complete_bingo_cards)

@app.route('/update/bingo_square/<int:square_id>/<int:user_id>')
def update_bingo_square(square_id, user_id):
    update_query = 'UPDATE BingoSquare SET user_id = ? where id = ?'
    cur = get_db().execute(update_query, [user_id, square_id])
    get_db().commit()

    # check if we get a bingo

    return 'Updated bingo square'

