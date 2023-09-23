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

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()

    if request.method == 'GET':
        all_messages = []
        for message in messages:
            message_dict = message.to_dict()
            all_messages.append(message_dict)
        
        response = make_response(jsonify(all_messages), 200)
        return response
    
    elif request.method == 'POST':
        new_message = Message(
            body=request.get_json().get("body"),
            username=request.get_json().get("username"),
        )
        db.session.add(new_message)
        db.session.commit()

        new_message_dict = new_message.to_dict()

        response = make_response(new_message_dict, 201)
        return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    # updates the body of the message using params and returns the updated message as json
    if request.method == 'PATCH': 
        for attr in request.form:
            setattr(message, attr, request.form.get(attr))
        
        db.session.add(message)
        db.session.commit()

        message_dict = message.to_dict()

        response = make_response(jsonify(message_dict), 200)
        return response
    # deletes the message from the database
    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message successfully deleted."
        }

        response = make_response(response_body, 200)

        return response

if __name__ == '__main__':
    app.run(port=5555)
