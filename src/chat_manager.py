from flask import redirect, request, jsonify, make_response
import traceback
from database.todo import create_room_id

from . import app

@app.route('<host>/chats/new', methods=['POST'])
def create_room():
    try:
        create_room_id()
        return jsonify({
            'room_id': 'Hello world!',
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})
