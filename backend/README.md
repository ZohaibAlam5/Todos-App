---
title: Todo Backend
emoji: 🚀
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# Todo Backend API

This is the backend API for the Todo application, built with FastAPI.

## Configuration

Environment variables needed:

- `DATABASE_URL`: PostgreSQL database connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `BETTER_AUTH_SECRET`: Secret for better auth
- `FRONTEND_URL`: URL of the frontend application
- `SMTP_SERVER`: SMTP server for email (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP port (e.g., 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password or app password
- `EMAIL_FROM`: Email address to send from

## Ports

The application runs on port 7860.

## Resources

This application requires minimal resources to run efficiently.