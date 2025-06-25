# Agentic Coding Assistant

A simple Python agent that can help you fix bugs, refactor, and add features to your own code. Inspired by tools like Cursor and Claude Code.

## Setup

``` bash
git clone https://github.com/danalytis/ai-coding-assistant.git
cd ai-coding-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

REQUIRED: Add your Google Gemini API key to a .env file in the project root:

``` 
GEMINI_API_KEY=your-google-api-key-here
```
## Usage

To run the agent in one-shot mode:
```
python main.py "your prompt here"
```
To run the agent in interactive mode:
```
python main.py --ineractive
```
To see token usage in either modes use the --verbose flag.
