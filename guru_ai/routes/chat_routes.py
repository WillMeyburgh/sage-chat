from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from guru_ai.ai import AI
from guru_ai.chat import Chat
from guru_ai.model.sage import Sage

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/get_sages', methods=['GET'])
@login_required
def get_sages():
    sages_data = []
    for sage_obj in Sage.get_all_sages(): # Iterate directly over the list of Sage objects
        sages_data.append({
            'name': sage_obj.name,
            'portrait_url': sage_obj.portrait_url
        })
    return jsonify(sages_data)

@chat_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get('message')
    selected_sage_name = request.json.get('sage', 'Socrates') # Default to Socrates

    sage = Sage.get_sage(selected_sage_name)
    chat = Chat(current_user, sage)
    sage_response = AI.get().message(chat, user_message)
    chat.update()
    return jsonify({'response': sage_response, 'sage': selected_sage_name})

@chat_bp.route('/get_initial_message', methods=['POST'])
@login_required
def get_initial_message():
    selected_sage_name = request.json.get('sage', 'Socrates') # Default to Socrates
    sage = Sage.get_sage(selected_sage_name)
    chat = Chat(current_user, sage)
    if chat.info is not None and f'\n{current_user.name}: ' in chat.info.prompt_text:
        chat.update_system_instruction(AI.get())

    if chat.info is None or chat.info.system_instruction is None:
        initial_message = sage.initial_message
    else:
        initial_message = AI.get().ask("Write a intruduction for your new chat, keep it short (less than 40 words)", chat.system_instruction)

    chat.sage_message(initial_message)
    chat.update()
        
    return jsonify({'initial_message': initial_message, 'sage': selected_sage_name})
