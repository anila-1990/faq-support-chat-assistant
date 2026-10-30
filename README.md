![Tests](https://github.com/anila-1990/faq-support-chat-assistant/actions/workflows/tests.yml/badge.svg)
**Live demo:** https://your-app-name.onrender.com/chat


# FAQ Support Assistant

A small Python web app that answers support questions from a stored FAQ list.

## Features
- REST API built with FastAPI
- Keyword-based question matching
- Simple web chat page

## Run locally
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/chat

## Built with
Python, FastAPI, Uvicorn