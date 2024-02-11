from openai import OpenAI
import time
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

"""
Main function: conversation logic
"""
def ai_conversation():

    system_prompt_ai1 = "You are a knowledgeable and articulate assistant. You are talking to other AI. RESPOND WITH SHORT, CONVERSATIONAL MESSAGES."
    system_prompt_ai2 = "You are a creative and curious assistant. Start by asking what the AI alignment is. You are talking to other AI. RESPOND WITH SHORT, CONVERSATIONAL MESSAGES."
    
    history_ai1 = [{"role": "system", "content": system_prompt_ai1}]
    history_ai2 = [{"role": "system", "content": system_prompt_ai2}]

    """Conversation Loop"""
    while True:
        """ AI 1 Response"""
        if history_ai2[-1]['role'] == "assistant":
            history_ai1.append({"role": "user", "content": history_ai2[-1]['content']})

        response_ai1 = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=history_ai1,
            stream=True
        )
        ai1_reply = ''
        print('AI 1: ',end='')
        for chunk in response_ai1:
            ai1_reply_chunk = chunk.choices[0].delta.content
            if ai1_reply_chunk:
                ai1_reply += ai1_reply_chunk
                print(ai1_reply_chunk,end='')
        print()
        print()
        history_ai1.append({"role": "assistant", "content": ai1_reply})
        """ AI 2 Response"""
        history_ai2.append({"role": "user", "content": ai1_reply})
        response_ai2 = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=history_ai2,
            stream=True
        )
        ai2_reply = ''
        print('AI 2: ',end='')
        for chunk in response_ai2:
            ai2_reply_chunk = chunk.choices[0].delta.content
            if ai2_reply_chunk:
                ai2_reply += ai2_reply_chunk
                print(ai2_reply_chunk,end='')
        print()
        print()
        history_ai2.append({"role": "assistant", "content": ai2_reply})

        """optional delay - gpt 3.5 generates responses really quickly"""
        time.sleep(2)

ai_conversation()