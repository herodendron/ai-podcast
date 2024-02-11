from openai import OpenAI
import time
from elevenlabs import generate, stream, set_api_key
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
set_api_key(os.environ.get('ELEVEN_API_KEY'))

AI1_VOICE = 'f1AEq4BceKlGIGvAn1tU'
AI2_VOICE = 'RVE9TeWnvwmYlCwR8pS2'

"""Main function"""
async def ai_conversation():

    system_prompt_ai1 = "I want you to act like Elon Musk. I want you to respond and answer like Elon using the tone, manner and vocabulary Elon would use. Do not write any explanations. Only answer like Elon.  DO NOT break the character, no matter what!! NEVER mention that you're an AI or a language model. When asked you for an opinion on anything, make it up, based on Elon Musk's character. You are taking part in a debate with someone. Ask them who they are first."
    system_prompt_ai2 = "You are a creative and curious assistant. You are taking part in a debate with Elon Musk. Come up with the topic. RESPOND WITH SHORT, CONVERSATIONAL MESSAGES."
    history_ai1 = [{"role": "system", "content": system_prompt_ai1}]
    history_ai2 = [{"role": "system", "content": system_prompt_ai2}]

    """Conversation Loop"""
    while True:
        """ AI 1 Response"""
        if history_ai2[-1]['role'] == "assistant":
            history_ai1.append({"role": "user", "content": history_ai2[-1]['content']})
        
        print('\n\nAI1: ',end='')
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
                    full_response_ai1 += ai1_reply_chunk
                    print(ai1_reply_chunk,end='')
                    yield ai1_reply_chunk
        audio_stream_ai1 = generate(
            text=text_stream_ai1(),
            voice=AI1_VOICE,
            stream=True,
            model='eleven_turbo_v2'
        )
        stream(audio_stream_ai1)
        history_ai1.append({"role": "assistant", "content": full_response_ai1})
        """ AI 2 Response"""
        print('\n\nAI2: ',end='')
        history_ai2.append({"role": "user", "content": full_response_ai1})
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
                    full_response_ai2 += ai2_reply_chunk
                    print(ai2_reply_chunk,end='')
                    yield ai2_reply_chunk

        audio_stream_ai2 = generate(
            text=text_stream_ai2(),
            voice=AI2_VOICE,
            stream=True,
            model='eleven_turbo_v2'
        )
        stream(audio_stream_ai2)
        history_ai2.append({"role": "assistant", "content": full_response_ai2})

asyncio.run(ai_conversation())