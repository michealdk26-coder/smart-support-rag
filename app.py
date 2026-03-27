
from flask import Flask, render_template, request, jsonify
import PyPDF2
from groq import Groq
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

app = Flask(__name__)
client = Groq(api_key=GROQ_API_KEY)

document_chunks = []

def load_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def split_into_chunks(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def find_relevant_chunks(question, chunks, top_n=3):
    question_words = set(question.lower().split())
    scored_chunks = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(question_words.intersection(chunk_words))
        scored_chunks.append((score, chunk))
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return [chunk for score, chunk in scored_chunks[:top_n]]

def ask_llm(question, relevant_chunks, file_type="document"):
    context = "\n\n".join(relevant_chunks)
    prompt = f"""You are a helpful assistant that ONLY answers questions based on the uploaded {file_type}.

IMPORTANT RULES:
- ONLY answer questions related to the uploaded {file_type}
- If the question is NOT related to the {file_type}, respond with:
  "Please ask questions related to the uploaded {file_type} only."
- Format your answers neatly with clear paragraphs and bullet points
- Give detailed and well structured answers

Context from {file_type}:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that only answers questions based on the uploaded {file_type}. Format answers neatly with proper spacing and structure."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1000
    )
    return response.choices[0].message.content

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global document_chunks
    file = request.files["file"]
    filename = file.filename

    # Read file directly without saving
    if filename.endswith(".pdf"):
        import io
        file_bytes = io.BytesIO(file.read())
        reader = PyPDF2.PdfReader(file_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    elif filename.endswith(".txt"):
        text = file.read().decode("utf-8")
    else:
        return jsonify({"error": "Unsupported file type! Please use PDF or TXT"})

    document_chunks = split_into_chunks(text)
    return jsonify({"message": f"✅ File loaded successfully! Split into {len(document_chunks)} chunks"})


@app.route("/ask", methods=["POST"])
def ask():
    global document_chunks
    data = request.json
    question = data.get("question")

    if not document_chunks:
        return jsonify({"error": "Please upload a file first!"})

    relevant_chunks = find_relevant_chunks(question, document_chunks)
    answer = ask_llm(question, relevant_chunks)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
