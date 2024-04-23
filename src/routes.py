from flask import redirect, request, jsonify, make_response
import traceback

from . import app

@app.route('/test', methods=['GET'])
def hello_world():
    try:
        return jsonify({
            'test': 'Hello world!',
            'status': 'OK'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

