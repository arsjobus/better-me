# better-me
Tasking Management with AI as an Accountability Coach

Run an AI Coach locally using Ollama and model of your choice

## Use Cases

As a user, I want to manage a list of tasks from multiple devices,
So that I can access and update my task completion.

As a user, I want to be notified by an AI Coach interruptively,
So that I can be reminded to complete every task.

As a user, I want my tasks to reset to be incomplete at 8 AM tomorrow,
So that I can be reminded to complete my tasks everyday.

## App

This App allows the users to create and manage tasks.

1) CD into 'app' directory.
2) Install dependencies `npm install`
3) Copy `.env-example` to `.env`
4) In the .env file, fill in 'VUE_APP_API_BASE_URL' as http://localhost:3000 or Vercel API URL.
5) Run locally with `npm run serve`

## API

This API is consumed by the App.

1) CD into 'api' directory.
2) Install dependencies `npm install`
3) Copy `.env-example` to `.env`
4) In the .env file, fill in 'REDIS_URL' as the local or remote Redis Base URL.
5) In the .env file, fill in 'REDIS_TOKEN' as token / password used to authenticate to Redis.
6) In the .env file, fill in 'JWT_SECRET' as a strong JWT sercet.
7) In the .env file, fill in 'ADMIN_USERNAME' as a username of your choice.
8) In the .env file, fill in 'ADMIN_PASSWORD' as a password of your choice.
9) Run locally with `vercel dev`

Note: Username / Password used to login to the app.

## AI Coach

AI Coach uses TTS to speak aloud the coaching text output from LLM service.

### Prerequisites

Install Ollama and pull model as llama3.2 or the model you want to use!

1) CD into 'coach' directory.
2) Make venv `python -m venv .venv`
3) Install dependencies `pip install`
4) In the .env file, fill in 'OLLAMA_API_URL' as the localhost ollama API host url + port number.
5) In the .env file, fill in 'OLLAMA_MODEL' as the model name that you want to use as the AI Coach.
6) In the .env file, fill in 'REDIS_URL' as the local or remote Redis Base URL.
7) In the .env file, fill in 'REDIS_TOKEN' as token / password used to authenticate to Redis.
8) Run with `python main.py` - should schedule this to run periodically to check-in
9) Configure task scehduler service to run 'main.vbs' as often as you want coach to check-in on you.

Alternatively Deploy Docker Locally

1) `docker build -t ollama-service .`
2) `docker run -p 11434:11434 ollama-service`

Finished.