# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django REST API backend for "Drafted" - an AI-powered application that helps users match their activities and experiences to job application questions. The system uses OpenAI embeddings and vector similarity search through Supabase/PostgreSQL with pgvector to suggest relevant activities based on application questions.

## Development Commands

### Environment Setup
- Virtual environment is in `venv/` directory
- Activate with: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`

### Database Operations
- Run migrations: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`
- Create superuser: `python manage.py createsuperuser`

### Development Server
- Run development server: `python manage.py runserver`
- Access admin panel: http://localhost:8000/admin/
- API documentation (Swagger): http://localhost:8000/swagger/
- ReDoc documentation: http://localhost:8000/redoc/

### Testing
- Run all tests: `python manage.py test`
- Run specific app tests: `python manage.py test <app_name>`

## Architecture

### Database Configuration
- **Primary Database**: PostgreSQL on Supabase
- **Vector Search**: Uses pgvector extension for embedding similarity search
- **Authentication**: Will be handled by Clerk (currently has legacy Supabase auth integration)

### Django Apps Structure

#### Core Apps
- **users/**: User profiles (currently has Supabase auth integration, will migrate to Clerk)
- **activities/**: User activities, events, and embeddings storage
- **applications/**: Job applications and question management
- **ai/**: AI-powered question analysis and activity matching

#### Key Models
- `users.Profile`: User profile data (currently linked to Supabase auth, will be updated for Clerk)
- `users.SupabaseUser`: Legacy Supabase user model (will be replaced with Clerk integration)
- `activities.ActivityEmbedding`: Vector embeddings for activities (1536 dimensions)
- `activities.Activity`: User activities with metadata
- `activities.Event`: Detailed events within activities (STAR method structure)
- `applications.Application`: Job applications
- `applications.QuestionList`: Application questions
- `ai.EventSuggestion`: AI-generated activity suggestions

### AI Integration
- **OpenAI API**: Used for text embeddings (text-embedding-3-small model)
- **Vector Search**: Supabase RPC function `match_documents` for similarity search
- **Chunking**: Text is chunked to 8000 tokens max using tiktoken
- **Similarity Threshold**: 0.3 minimum threshold, returns top 3 matches

### API Endpoints
- `/api/ai/`: AI-powered question analysis endpoints
- `/api/activities/`: Activity and event management (currently commented out in URLs)
- `/admin/`: Django admin interface
- `/swagger/`, `/redoc/`: API documentation

## Environment Variables

Required environment variables (stored in `.env`):
- `SECRET_KEY`: Django secret key
- `DB_PASSWORD`: Supabase database password
- `DB_URL`: Supabase project URL
- `DB_KEY`: Supabase anon/service key
- `OPENAI_KEY`: OpenAI API key

## Key Implementation Details

### Vector Similarity Search
The system uses a custom Supabase RPC function `match_documents` that performs cosine similarity search on activity embeddings. The search returns activities with similarity scores and metadata.

### Activity Parsing
The `parse_ai_suggestion_to_json` function converts raw embedding search results into structured JSON with ability lists and activity matches, including fit scores.

### STAR Method Integration
Events are structured to support the STAR method (Situation, Task, Action, Result) with additional fields for contribution and event roles.

### Database Integration
- Uses Supabase PostgreSQL for database and vector search
- Currently has Supabase auth integration that will be replaced with Clerk
- Database schema spans both public and auth schemas (auth schema access will change with Clerk migration)

## Development Notes

- Authentication will be migrated from Supabase to Clerk
- Activities API endpoints are currently commented out in the main URL configuration
- Several utility scripts exist in the root directory for data processing and testing
- The system uses Django REST Framework with drf-yasg for API documentation
- User model and authentication flow will need updates for Clerk integration