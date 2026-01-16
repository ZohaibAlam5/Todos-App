# Configuration file for the application

import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "a-string-secret-at-least-256-bits-long")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@taskflow.com")

# Gemini API Configuration (for AI Chatbot via OpenAI-compatible endpoint)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Trailing slash required per Google's documentation
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# Available models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")