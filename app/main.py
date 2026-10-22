from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.data import FAQS

app = FastAPI(title="FAQ Support Assistant")

# Common words we ignore when matching, because they appear in almost every question
STOP_WORDS = {"how", "do", "i", "my", "the", "a", "is", "to", "what", "your", "can", "me", "you", "of", "for", "in", "an", "it", "am", "and", "or", "on"}


def get_words(text):
    text = text.lower()
    for mark in ["?", ".", ",", "'", "!"]:
        text = text.replace(mark, "")
    return {word for word in text.split() if word not in STOP_WORDS}


@app.get("/")
def home():
    return {"message": "Hello, the FAQ assistant is running!"}


@app.get("/faqs")
def list_faqs():
    return FAQS


@app.get("/ask")
def ask(question: str):
    user_words = get_words(question)

    best_faq = None
    best_score = 0

    for faq in FAQS:
        searchable_text = faq["question"] + " " + " ".join(faq["keywords"])
        faq_words = get_words(searchable_text)
        score = len(user_words & faq_words)
        if score > best_score:
            best_score = score
            best_faq = faq

    if best_faq is None:
        return {"answer": "Sorry, I couldn't find an answer. Please contact support."}

    return {"answer": best_faq["answer"], "matched_question": best_faq["question"]}


PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>FAQ Support Assistant</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 500px; margin: 60px auto; }
    input { width: 70%; padding: 8px; }
    button { padding: 8px 16px; }
    #answer { margin-top: 20px; padding: 12px; background: #eef6f7; display: none; }
  </style>
</head>
<body>
  <h2>Support Assistant</h2>
  <input id="question" placeholder="e.g. how do I reset my password?">
  <button onclick="ask()">Ask</button>
  <div id="answer"></div>

  <script>
    async function ask() {
      const question = document.getElementById("question").value;
      const response = await fetch("/ask?question=" + encodeURIComponent(question));
      const data = await response.json();
      const box = document.getElementById("answer");
      box.style.display = "block";
      box.textContent = data.answer;
    }
  </script>
</body>
</html>
"""


@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return PAGE