#  Smart Support Knowledge Base (RAG)

## Description
A script that allows users to ask questions about
PDF and TXT files using Groq AI for free.

## Features
- Supports PDF and TXT files
- Beautiful HTML/CSS/JS frontend
- Powered by Groq AI (Free)
- Simple question answering

## How to Run


### 1. Clone the repository
git clone git remote add origin https://github.com/michealdk26-coder/smart-support-rag.git
cd smart-support-rag

### 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add your Groq API key
cp config.example.py config.py
nano config.py

### 5. Run the app
python app.py

### 6. Open browser
http://127.0.0.1:5000
