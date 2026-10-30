from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page_works():
    response = client.get("/")
    assert response.status_code == 200


def test_faq_list_is_not_empty():
    response = client.get("/faqs")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_password_question_finds_password_answer():
    response = client.get("/ask", params={"question": "I forgot my password"})
    assert response.status_code == 200
    assert "password" in response.json()["matched_question"].lower()


def test_keyword_matching_works():
    response = client.get("/ask", params={"question": "how do I unsubscribe"})
    assert "cancel" in response.json()["matched_question"].lower()


def test_unknown_question_gets_fallback_message():
    response = client.get("/ask", params={"question": "xyzabc"})
    assert "Sorry" in response.json()["answer"]


def test_missing_question_is_rejected():
    response = client.get("/ask")
    assert response.status_code == 422


def test_adding_faq_without_admin_key_is_blocked():
    new_faq = {"question": "Test question?", "answer": "Test answer."}
    response = client.post("/faqs", json=new_faq)
    assert response.status_code == 401