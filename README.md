# AI Podcast / Conversation

## Overview

This fun project simulates a conversation between two AIs. It includes three versions:

1. **main-text.py**: Basic text output of the conversation.
2. **main-voice.py**: Adds ElevenLabs voice simulation to the conversation.
3. **main-web.py**: Provides a web interface for the conversation using Flask and SocketIO.

![Untitled](https://cdn.discordapp.com/attachments/1058750255144906887/1206257755707547758/image.png?ex=65db5a14&is=65c8e514&hm=bb5d9e7b622dfcc5d5253851f878b7a90d2e93045b846610dd6226f1b1722a7c&)

## Requirements

- Python 3
- Flask
- Flask-SocketIO
- OpenAI API
- ElevenLabs API

## Setup

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set your OpenAI and ElevenLabs API keys in the `.env` file.
4. Install mpv, necessary to stream audio. Install instructions: https://mpv.io/installation/
5. Run the desired version of the application (web version recommended!)

## Usage

- **main-text.py**: Run `python main-text.py` to start the text-based conversation.
- **main-voice.py**: Run `python main-voice.py` for voice simulation.
- **main-web.py**: Run `python main-web.py` and visit `http://127.0.0.1:5000/` for the web interface.

## Configuration

Edit the system prompts/voice IDs in `main-text.py`  and `main.voice.py`
Edit the `CONFIG` dictionary in `main-web.py` to customize the AI characters and voices.
