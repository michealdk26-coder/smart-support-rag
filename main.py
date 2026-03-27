import os
import PyPDF2
from groq import Groq
from config import GROQ_API_KEY


client = Groq(api_key=GROQ_API_KEY)


def load_pdf(file_path):
    print(f"\n📄 Loading PDF: {file_path}")
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text += page.extract_text()
            print(f"   Loaded page {page_num + 1}")
    return text

-
def load_txt(file_path):
    print(f"\n📄 Loading TXT file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"    Text file loaded successfully")
    return text


def load_file(file_path):
    if file_path.endswith(".pdf"):
        return load_pdf(file_path)
    elif file_path.endswith(".txt"):
        return load_txt(file_path)
    else:
        print(" Unsupported file type! Please use PDF or TXT")
        return None


def split_into_chunks(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    print(f"\n✂️  Split into {len(chunks)} chunks")
    return chunks


def find_relevant_chunks(question, chunks, top_n=3):
    question_words = set(question.lower().split())
    scored_chunks = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(question_words.intersection(chunk_words))
        scored_chunks.append((score, chunk))
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [chunk for score, chunk in scored_chunks[:top_n]]
    return top_chunks


def ask_llm(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = f"""You are a helpful assistant.
Use the following context from a document to answer the question.
If the answer is not in the context, say "I could not find that in the document."

Context:
{context}

Question: {question}

Answer:"""

    print("\n Asking Groq AI...")

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


def main():
    print("=" * 50)
    print("   Smart Support Knowledge Base (RAG)")
    print("=" * 50)
    print("\n  Supported file types: PDF and TXT")
    print("=" * 50)

    file_path = input("\n Enter the path to your file (PDF or TXT): ")

    if not os.path.exists(file_path):
        print(" File not found! Please check the path.")
        return

    text = load_file(file_path)

    if text is None:
        return

    chunks = split_into_chunks(text)

    print("\n File loaded successfully!")
    print("\n" + "=" * 50)

    while True:
        print("\n💬 Ask a question about your document")
        print("   (Type 'quit' to exit)")
        question = input("\nYour question: ")

        if question.lower() == "quit":
            print("\n Goodbye!")
            break

        if not question.strip():
            print(" Please enter a valid question")
            continue

        relevant_chunks = find_relevant_chunks(question, chunks)
        answer = ask_llm(question, relevant_chunks)

        print("\n" + "=" * 50)
        print(f" Answer:\n{answer}")
        print("=" * 50)

if __name__ == "__main__":
    main()
