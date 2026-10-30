import os
from fastapi import FastAPI,Header,HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# from app.data import FAQS
from app.database import init_db,get_all_faqs,add_faq

app = FastAPI(title="FAQ Support Assistant")
ADMIN_KEY = os.getenv("ADMIN_KEY","")
init_db()

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
    return get_all_faqs()

class NewFAQ(BaseModel):
    question: str = Field(min_length=3)
    answer: str = Field(min_length=3)
    keywords: list[str] = []


@app.post("/faqs")
def create_faq(faq: NewFAQ, x_admin_key: str = Header(default="")):
    if ADMIN_KEY == "" or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Wrong admin key")
    new_id = add_faq(faq.question, faq.answer, faq.keywords)
    return {"id": new_id, "message": "FAQ added"}


@app.get("/ask")
def ask(question: str):
    user_words = get_words(question)

    best_faq = None
    best_score = 0

    for faq in get_all_faqs():
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
      const question = document.getElementById("question").value.trim();
      if (question === "") {
        return;
      }
      const response = await fetch("/ask?question=" + encodeURIComponent(question));
      const data = await response.json();
      const box = document.getElementById("answer");
      box.style.display = "block";
      box.textContent = data.answer;
    }

    document.getElementById("question").addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        ask();
      }
    });
  </script>
</body>
</html>
"""


@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return PAGE

ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Add FAQ</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 500px; margin: 60px auto; }
    input, textarea { width: 100%; padding: 8px; margin: 6px 0 14px 0; box-sizing: border-box; }
    button { padding: 8px 16px; }
    #message { margin-top: 16px; color: green; }
  </style>
</head>
<body>
  <h2>Add a new FAQ</h2>
  <label>Admin key</label>
  <input id="adminKey" type="password" placeholder="Enter admin key">
  <label>Question</label>
  <input id="question" placeholder="e.g. Do you offer a free trial?">

  <label>Answer</label>
  <textarea id="answer" rows="3"></textarea>

  <label>Keywords (separate with commas)</label>
  <input id="keywords" placeholder="trial, free, demo">

  <button onclick="saveFaq()">Save FAQ</button>
  <div id="message"></div>

  <script>
    async function saveFaq() {
      const keywordText = document.getElementById("keywords").value;
      const keywords = keywordText.split(",").map(k => k.trim()).filter(k => k !== "");

      const response = await fetch("/faqs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-key": document.getElementById("adminKey").value
        },
        body: JSON.stringify({
          question: document.getElementById("question").value,
          answer: document.getElementById("answer").value,
          keywords: keywords
        })
      });

      const message = document.getElementById("message");
      if (response.ok) {
        message.style.color = "green";
        message.textContent = "FAQ saved!";
        document.getElementById("question").value = "";
        document.getElementById("answer").value = "";
        document.getElementById("keywords").value = "";
      } else {
        message.style.color = "red";
        message.textContent = "Could not save. Question and answer need at least 3 characters.";
      }
    }
  </script>
</body>
</html>
"""


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return ADMIN_PAGE