# Architecture & Design Explanation

## Technical Stack
- **Backend**: Django (Python) - chosen for its robust authentication and rapid development capabilities.
- **Database**: MySQL - used for structured storage of users, projects, prompts, and chat history.
- **AI Integration**: OpenRouter API (`mistralai/mistral-7b-instruct`) - selected for high performance and low latency.
- **Frontend**: Vanilla HTML/CSS with JavaScript - implemented with a "Glassmorphism" design system for a premium aesthetic without external heavy libraries.

## Data Model
1. **User**: Standard Django user model for authentication.
2. **Project**: Central entity owned by a User.
3. **Prompt**: Versioned system instructions for the AI agent within a project.
4. **ChatMessage**: Persistent storage of user and assistant interactions.
5. **ProjectFile**: Local storage of files associated with an agent's knowledge base.

## Design Decisions
- **Session & DB Hybrid**: Real-time project chats are saved to the Database for persistence, while global sessions are used for temporary state where appropriate.
- **Async Feedback**: The chat UI uses asynchronous `fetch` calls with custom loading indicators to ensure the interface never feels "stuck" during AI processing.
- **Security**: Environment variables (`.env`) and Django's built-in protection mechanisms (CSRF, @login_required) are used to protect user data and API keys.

## Non-Functional Requirements
- **Scalability**: The relational schema supports multiple projects per user and multiple users concurrently.
- **Performance**: Optimized request timeouts (20s) and model selection (Mistral 7B) ensure snappy responses.
