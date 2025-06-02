from flask import Blueprint, request, jsonify
from guru_ai.ai import AI
from guru_ai.chat import Chat
from guru_ai.model.sage import Sage

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/get_sages', methods=['GET'])
def get_sages():
    sages_data = []
    for sage_obj in Sage.get_all_sages(): # Iterate directly over the list of Sage objects
        sages_data.append({
            'name': sage_obj.name,
            'portrait_url': sage_obj.portrait_url
        })
    return jsonify(sages_data)

chats = {}

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    selected_sage_name = request.json.get('sage', 'Socrates') # Default to Socrates

    sage = Sage.get_sage(selected_sage_name)
    if sage.name not in chats:
        chats[sage.name] = Chat(sage)
    
    sage_response = AI.get().message(chats[sage.name], user_message)
    return jsonify({'response': sage_response})

@chat_bp.route('/get_initial_message', methods=['POST'])
def get_initial_message():
    selected_sage_name = request.json.get('sage', 'Socrates') # Default to Socrates
    sage = Sage.get_sage(selected_sage_name)
    initial_message = sage.initial_message # Use initial_message for display
    return jsonify({'initial_message': initial_message}) # Keep key as initial_prompt for frontend compatibility
