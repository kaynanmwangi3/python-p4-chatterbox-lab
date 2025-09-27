from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()

    if not messages:
        return make_response(jsonify("no messages found"), 200)
    return make_response(jsonify([message.to_dict() for message in messages]), 200)

@app.route('/messages', methods=['POST'])
def update_messages():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')

    if not body and username:
        return make_response(jsonify("body and username required"), 400)

    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()
    return make_response(jsonify(new_message.to_dict()), 201)


@app.route('/messages/<int:id>', methods=['PATCH'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if not message:
        return make_response(jsonify("message not found"), 404)

    data = request.get_json()
    new_message_body = data.get('body')
    if not new_message_body:
        return make_response(jsonify("body required"), 400)
    message.body = new_message_body
    db.session.commit()
    return make_response(jsonify(message.to_dict()), 200)

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.filter_by(id=id).first()
    if not message:
        return make_response(jsonify("message not found"), 404)

    db.session.delete(message)
    db.session.commit()
    return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555)
