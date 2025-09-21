# Truby AI

### ⚠️ This application is under development.

Truby AI is your AI-assistant for writing better screenplays. If you want to flesh out your screenplay and have sample screenplays, then you can use Truby AI to provide you with screenwriting and storytelling tips!

## Tech Stack at a Glance

The tech stack for this application is as follows:
- **FastAPI** and **SQLModel** for the backend.
- Local **SQLite3**.
- **Pinecone** for the vector database.
- **MongoDB** for the document data store for the scenes we extract from the screenplay.
- **OpenAI** for the embeddings and LLM inference.
- **The Movie Database** as our gold source for movie data.
- Coming Soon: **MCP** to integrate with a foundational LLM of your choice.

## Important Environment Variables

This project will require a `.env` file with several variables. You may refer to the `.env.example` as it contains a description of each variable and its purpose. We produce it below for convenience:

- `OPENAI_API_KEY`: You'll need an OpenAI API key.
- `PINECONE_API_KEY`: Pinecone API key: you can get one for free + a free index.
- `PINECONE_HOST_URL`: Pinecone Host URL: you'll get one once you create a free index.
- `TMDB_READONLY_API_KEY`: The Movie Database read-only API key.
- `SQL_DB_PATH`: Location of your SQL database file. For this project, a local SQLite3 database is assumed.
- `MONGODB_CONNECTION`: MongoDB connection string.
- `MONGODB_DATABASE`: MongoDB database name.

## Getting Started

To be written.