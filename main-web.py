from flask import Flask, render_template
from flask_socketio import SocketIO
from openai import OpenAI
from elevenlabs import generate, stream, set_api_key
import asyncio
import threading
import os
from dotenv import load_dotenv
from colorama import init
load_dotenv()
init()


CONFIG = {
    'openai_api_key': os.environ.get('OPENAI_API_KEY'),
    'elevenlabs_api_key': os.environ.get('ELEVEN_API_KEY'),
    'ai1': {
        'name': 'Elon Musk',
        'system_prompt': "I want you to act like Elon Musk. I want you to respond and answer like Elon using the tone, manner and vocabulary Elon would use. Do not write any explanations. Only answer like Elon.  DO NOT break the character, no matter what!! NEVER mention that you're an AI or a language model. When asked you for an opinion on anything, make it up, based on Elon Musk's character. You are taking part in a debate with someone. Ask them who they are first.",
        'profile_pic_url': 'https://singifyai.fineshare.com/song-ai/covers/elon-musk.webp',
        'voice_id': 'Daniel', # recommended to replace with a voice id of your selection
    },
    'ai2': {
        'name': 'Creative Assistant',
        'system_prompt': "You are a creative and curious assistant. You are taking part in a debate with Elon Musk. Come up with the topic. RESPOND WITH SHORT, CONVERSATIONAL MESSAGES.",
        'profile_pic_url': 'https://ichef.bbci.co.uk/news/976/cpsprodpb/16620/production/_91408619_55df76d5-2245-41c1-8031-07a4da3f313f.jpg',
        'voice_id': 'Glinda', # recommended to replace with a voice id of your selection
    }
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
conversation_active = False

"""
Colored Prints class
"""
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


"""Inits"""
client = OpenAI(api_key=CONFIG['openai_api_key'])
set_api_key(CONFIG['elevenlabs_api_key'])

"""
Conversation Logic
"""
async def ai_conversation():
    """Define system prompts and init conversations"""
    history_ai1 = [{"role": "system", "content": CONFIG['ai1']['system_prompt']}]
    history_ai2 = [{"role": "system", "content": CONFIG['ai2']['system_prompt']}]

    """Conversation Loop"""
    while True:

        socketio.emit('ai_state', {'ai_id': 'ai1', 'state': 'Thinking'})
        socketio.emit('ai_state', {'ai_id': 'ai2', 'state': 'Listening'})

        """ AI 1 Response"""
        print(f"{Colors.OKCYAN}AI 1: {Colors.ENDC}",end='')
        if history_ai2[-1]['role'] == "assistant":
            history_ai1.append({"role": "user", "content": history_ai2[-1]['content']})
        """text"""
        response_ai1 = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=history_ai1,
            stream=True
        )
        full_response_ai1 = ""

        def text_stream_ai1():
            nonlocal full_response_ai1
            for chunk in response_ai1:
                ai1_reply_chunk = chunk.choices[0].delta.content
                if ai1_reply_chunk:
                    print(ai1_reply_chunk, end='')
                    full_response_ai1 += ai1_reply_chunk.replace('\n', '')
                    socketio.emit('ai_message', {'ai1_partial_response': ai1_reply_chunk.replace('\n', ''), 'ai2_partial_response': ''})
                    yield ai1_reply_chunk
            socketio.emit('ai_message', {'ai1_response_end': True, 'ai2_response_end': False})
            print()

        socketio.emit('ai_state', {'ai_id': 'ai1', 'state': 'Talking'})
        """voice"""
        audio_stream_ai1 = generate(
            text=text_stream_ai1(),
            voice=CONFIG['ai1']['voice_id'],
            stream=True,
            model='eleven_turbo_v2'
        )
        stream(audio_stream_ai1)
        history_ai1.append({"role": "assistant", "content": full_response_ai1})

        socketio.emit('ai_message', {'ai1_response': full_response_ai1, 'ai2_response': ''})
        socketio.emit('ai_state', {'ai_id': 'ai1', 'state': 'Listening'})
        socketio.emit('ai_state', {'ai_id': 'ai2', 'state': 'Thinking'})

        """AI 2 Response"""
        print(f"{Colors.OKCYAN}AI 2: {Colors.ENDC}",end='')
        history_ai2.append({"role": "user", "content": full_response_ai1})
        """text"""
        response_ai2 = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=history_ai2,
            stream=True
        )
        full_response_ai2 = ""
        def text_stream_ai2():
            nonlocal full_response_ai2
            for chunk in response_ai2:
                ai2_reply_chunk = chunk.choices[0].delta.content
                if ai2_reply_chunk:
                    print(ai2_reply_chunk, end='')
                    full_response_ai2 += ai2_reply_chunk.replace('\n', '')
                    socketio.emit('ai_message', {'ai1_partial_response': '', 'ai2_partial_response': ai2_reply_chunk.replace('\n', '')})
                    yield ai2_reply_chunk
            socketio.emit('ai_message', {'ai1_response_end': False, 'ai2_response_end': True})
            print()
        socketio.emit('ai_state', {'ai_id': 'ai1', 'state': 'Talking'})

        """voice"""
        audio_stream_ai2 = generate(
            text=text_stream_ai2(),
            voice=CONFIG['ai2']['voice_id'],
            stream=True,
            model='eleven_turbo_v2'
        )
        stream(audio_stream_ai2)
        history_ai2.append({"role": "assistant", "content": full_response_ai2})
        socketio.emit('ai_message', {'ai1_response': '', 'ai2_response': full_response_ai2})


def start_ai_conversation():
    global conversation_active
    try:
        asyncio.new_event_loop().run_until_complete(ai_conversation())
    finally:
        conversation_active = False

@app.route('/')
def index():
    return render_template('index.html', 
                           ai1_pic=CONFIG['ai1']['profile_pic_url'], 
                           ai2_pic=CONFIG['ai2']['profile_pic_url'],
                           ai1_name=CONFIG['ai1']['name'],
                           ai2_name=CONFIG['ai2']['name'],

    )

"""socketio"""
@socketio.on('connect')
def on_connect():
    global conversation_active
    print(f"{Colors.OKBLUE}Client connected. Checking if debate needs to start.{Colors.ENDC}")

    if not conversation_active:
        print(f"{Colors.OKBLUE}Starting the debate.{Colors.ENDC}")
        conversation_active = True

        thread = threading.Thread(target=start_ai_conversation)
        thread.daemon = True
        thread.start()
    else:
        print(f"{Colors.OKBLUE}Debate is already ongoing.{Colors.ENDC}")

@socketio.on('disconnect')
def on_disconnect():
    print(f"{Colors.WARNING}Client disconnected{Colors.ENDC}")

if __name__ == '__main__':
    print(f"{Colors.HEADER}Booting up.. Visit http://127.0.0.1:5000/ to run the debate.{Colors.ENDC}")
    socketio.run(app, debug=True, use_reloader=False,port=5000)
