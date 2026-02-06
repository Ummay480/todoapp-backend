---
title: Todo Backend API
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo Backend API

A FastAPI-based todo application with AI capabilities.

## Features

- User authentication and authorization
- Task management (CRUD operations)
- AI-powered chatbot for natural language task management
- RAG (Retrieval Augmented Generation) integration
- Docker containerization

## API Endpoints

- `/api/auth/` - Authentication endpoints
- `/api/{user_id}/tasks` - Task management endpoints
- `/api/chatbot/` - AI chatbot endpoints
- `/health` - Health check endpoint

## Configuration

The application can be configured using environment variables. See `.env.example` for reference.

## Ports

- Application runs on port 7860
