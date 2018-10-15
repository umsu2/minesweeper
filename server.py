from flask import jsonify
from flask import Flask, session, request
from flask_session import Session
from minesweeper import Game
import redis
import os

SESSION_TYPE = 'redis'
r = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, db=0)
SESSION_REDIS = r

app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Session(app)

default_game = (10, 10, 10)


@app.route('/api/restart', methods=['POST'])
def restart():
    req = request.get_json()
    col = req['col']
    row = req['row']
    mines = req['mines']
    session['game'] = Game(row, col, mines)
    game_obj = session['game']
    return get_game_obj_response(game_obj)


@app.route('/api/get_current', methods=['GET'])
def get_current():
    if 'game' in session:
        game_obj = session['game']
        return get_game_obj_response(game_obj)
    return jsonify({})


def get_game_obj_response(game_obj):
    return jsonify(
        {"result": game_obj.print_board(False), "game_state": game_obj.state.name, "mines": game_obj.mines,
         "pieces_revealed": game_obj.pieces_revealed}, )


@app.route('/api/step_on', methods=['POST'])
def step_on():
    req = request.get_json()
    col = req['col']
    row = req['row']
    if 'game' not in session:
        session['game'] = Game(*default_game)
    game_obj = session['game']
    game_obj.step_on(row, col)
    session['game'] = game_obj
    return get_game_obj_response(game_obj)


@app.route('/api/toggle_flag', methods=['POST'])
def mark():
    req = request.get_json()
    col = req['col']
    row = req['row']
    if 'game' not in session:
        session['game'] = Game(*default_game)
    game_obj = session['game']
    game_obj.mark(row, col)
    session['game'] = game_obj
    return get_game_obj_response(game_obj)


if __name__ == "__main__":
    app.run()
