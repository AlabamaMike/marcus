# Marcus - A Philosophical AI Companion

Marcus is an interactive philosophical AI companion that embodies the wisdom traditions of Socratic inquiry and Stoic philosophy. Built with Google's Gemini AI and deployed on Google Cloud Platform, Marcus guides users toward self-knowledge, wisdom, and virtuous living through thoughtful dialogue.

## Overview

Named after the Stoic philosopher-emperor Marcus Aurelius, this application provides a modern web interface for engaging in philosophical conversations that challenge assumptions, promote critical thinking, and encourage personal growth through the ancient wisdom of Stoicism and the Socratic method.

## Features

### Core Functionality

- **Philosophical AI Dialogue**: Engage in meaningful conversations with an AI trained in Socratic questioning and Stoic wisdom
- **Persistent Session Management**: All conversations are saved to a local SQLite database with automatic session tracking
- **Session History**: Navigate through past conversations with an intuitive sidebar interface
- **Automatic Title Generation**: Sessions are automatically titled based on the initial conversation content
- **Multimodal Support**: Upload and discuss images alongside text conversations

### Configurable Tools

- **Google Search Integration**: Toggle real-time web search capabilities per session
- **Persistent Tool Preferences**: Tool settings are remembered for each session
- **Customizable AI Behavior**: Configure temperature, output length, and safety settings

### User Experience

- **Modern Web Interface**: Clean, responsive UI built with Gradio
- **Google Blue Theme**: Custom styling with Google Sans font
- **Streaming Responses**: Real-time message generation for natural conversation flow
- **Session Management**: Create, switch, and delete conversation sessions

## Technology Stack

### Backend
- **Python 3.11**: Primary programming language
- **Google GenAI SDK 1.5.0**: Integration with Google Vertex AI
- **Gradio 5.20.1**: Web UI framework for rapid prototyping
- **SQLite 3**: Lightweight database for session persistence
- **Pydantic**: Data validation and settings management

### AI/ML
- **Model**: Gemini 3 Pro Preview (via Google Vertex AI)
- **Location**: Global (Vertex AI Studio)
- **Configuration**:
  - Temperature: 1.0
  - Top-p: 0.95
  - Max output tokens: 65,535

### Infrastructure
- **Docker**: Containerization for consistent deployment
- **Google Cloud Run**: Serverless deployment platform
- **Google Cloud Project**: gp-ct-sbox-sat-gcp0bg-darksoft

## Prerequisites

- Python 3.11 or higher
- Google Cloud Platform account with Vertex AI API enabled
- Docker (optional, for containerized deployment)
- Git

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd marcus
   ```

2. **Install base tooling dependencies**
   ```bash
   pip install --require-hashes -r base-tooling-requirements.txt
   ```

3. **Install application dependencies**
   ```bash
   pip install --require-hashes -r requirements.txt
   ```

4. **Configure Google Cloud authentication**
   ```bash
   gcloud auth application-default login
   gcloud config set project gp-ct-sbox-sat-gcp0bg-darksoft
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the web interface**
   Navigate to `http://localhost:8080` in your web browser

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t marcus-ai .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 \
     -v ~/.config/gcloud:/root/.config/gcloud \
     marcus-ai
   ```

## Configuration

### Environment Variables

The application uses the following environment variables:

- `GRADIO_SERVER_PORT`: Server port (default: 8080)
- `GRADIO_SERVER_NAME`: Server binding address (default: 0.0.0.0)

### Google Cloud Configuration

Update the following in `app.py` if using a different GCP project:

```python
client = genai.Client(
    vertexai=True,
    project="your-project-id",  # Update this
    location="global",
)
```

### AI Model Settings

Model configuration can be adjusted in `app.py`:

```python
generation_config = {
    'temperature': 1.0,           # Creativity (0.0-2.0)
    'top_p': 0.95,                # Nucleus sampling
    'max_output_tokens': 65535,   # Maximum response length
}
```

## Usage

### Starting a Conversation

1. Launch the application
2. A new session will be created automatically
3. Type your message in the chat input
4. Optionally upload images to discuss visual content
5. Toggle Google Search if you need real-time information

### Managing Sessions

- **View History**: Click the session history sidebar to see past conversations
- **Switch Sessions**: Click any session title to load that conversation
- **Delete Sessions**: Use the delete button next to unwanted sessions
- **Session Titles**: Automatically generated from your first message

### Using the Socratic Method

Marcus is designed to guide you through self-discovery:

1. **Ask Open Questions**: Marcus will respond with clarifying questions
2. **Examine Assumptions**: Expect gentle challenges to your beliefs
3. **Reflect on Virtue**: Consider what wisdom, justice, courage, and temperance mean in your context
4. **Focus on Control**: Distinguish between what you can and cannot control

### Example Interactions

**Personal Challenge**
```
You: I'm struggling with a difficult decision at work
Marcus: What specifically troubles you about this situation?
         What aspects of this are within your direct control?
```

**Philosophical Inquiry**
```
You: What is the meaning of happiness?
Marcus: What leads you to seek happiness as a goal?
         How do you distinguish between pleasure and genuine flourishing?
```

## Project Structure

```
marcus/
├── app.py                          # Main application entry point
├── session_manager.py              # Session and message persistence
├── utils.py                        # Utility functions and theming
├── requirements.txt                # Python dependencies with hashes
├── base-tooling-requirements.txt   # Build tools (pip, setuptools, etc.)
├── Dockerfile                      # Container configuration
├── .gitignore                      # Git ignore patterns
├── README.md                       # This file
└── chat_sessions.db               # SQLite database (auto-generated)
```

### Key Components

#### `app.py` (407 lines)
- Main Gradio interface setup
- AI model initialization and configuration
- Message generation with streaming
- Session management integration
- Tool integration (web search)

#### `session_manager.py` (325 lines)
- SQLite database management
- Session CRUD operations
- Message persistence
- Tool preferences storage
- Automatic title generation

#### `utils.py` (232 lines)
- Authentication validation
- Custom theming (Google Blue)
- Helper functions
- UI utilities

## Database Schema

### Tables

**sessions**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `title`: TEXT (session name)
- `created_at`: TIMESTAMP (creation time)
- `updated_at`: TIMESTAMP (last activity)

**messages**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id`: INTEGER (foreign key)
- `role`: TEXT ('user' or 'assistant')
- `content`: TEXT (message content)
- `timestamp`: TIMESTAMP

**tool_preferences**
- `session_id`: INTEGER PRIMARY KEY
- `web_search_enabled`: BOOLEAN
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

## Development

### Adding New Features

1. Create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test locally
   ```bash
   python app.py
   ```

4. Commit and push
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

### Customizing the System Prompt

The philosophical framework is defined in the system instruction within `app.py`. To modify Marcus's personality or approach:

1. Locate the `si_text1` variable in `app.py`
2. Edit the system instruction text
3. Restart the application to apply changes

### Adding New Tools

To add new AI tools (like web search):

1. Update the `generate()` function in `app.py`
2. Add the tool to the Gradio interface
3. Store tool preferences in `session_manager.py`
4. Update the database schema if needed

## Deployment

### Google Cloud Run

The application is designed for deployment on Google Cloud Run:

1. **Ensure Docker image is built**
   ```bash
   docker build -t gcr.io/your-project/marcus-ai .
   ```

2. **Push to Google Container Registry**
   ```bash
   docker push gcr.io/your-project/marcus-ai
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy marcus-ai \
     --image gcr.io/your-project/marcus-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Production Considerations

- **Database Persistence**: Mount a persistent volume for `chat_sessions.db`
- **Authentication**: Implement proper user authentication for production use
- **Monitoring**: Set up Cloud Logging and Cloud Monitoring
- **Secrets Management**: Use Google Secret Manager for sensitive configuration
- **Rate Limiting**: Implement rate limiting to control API costs
- **HTTPS**: Cloud Run provides HTTPS by default

## Philosophical Framework

### Socratic Method Principles

Marcus employs the Socratic method by:
- Engaging through thoughtful questioning rather than direct instruction
- Helping users examine their beliefs and assumptions critically
- Acknowledging the limits of knowledge with intellectual humility
- Guiding users to discover truths through their own reasoning
- Challenging inconsistencies gently but persistently

### Stoic Wisdom Principles

Marcus embodies Stoic philosophy through:
- Distinguishing between what is within our control and what is not
- Focusing on developing virtue (wisdom, justice, courage, temperance)
- Encouraging emotional resilience through rational examination
- Promoting acceptance of fate (amor fati) while maintaining agency
- Grounding advice in practical application for daily life

## Security

- **Key Validation**: Requests are validated before processing
- **Hash Verification**: Dependencies are installed with hash verification
- **Safety Settings**: Configurable content safety filters
- **Warning System**: Alerts for unauthenticated access

## Troubleshooting

### Common Issues

**Database locked error**
```bash
# Remove the database lock
rm chat_sessions.db-journal
```

**Google Cloud authentication failed**
```bash
# Re-authenticate
gcloud auth application-default login
```

**Port already in use**
```bash
# Change the port in app.py or set environment variable
export GRADIO_SERVER_PORT=8081
```

**Module not found errors**
```bash
# Reinstall dependencies
pip install --require-hashes -r requirements.txt
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is generated based on Vertex AI Studio using Google GenAI Python SDK and Gradio. Please refer to your organization's licensing requirements.

## Acknowledgments

- **Marcus Aurelius**: For the inspiration and Stoic wisdom
- **Socrates**: For the method of inquiry
- **Google**: For Vertex AI and Gemini models
- **Gradio**: For the excellent web UI framework

## Support

For issues, questions, or suggestions:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed information

## Version History

- **Current**: Session history sidebar, web search toggle, persistent preferences
- **v0.2**: Added web search toggle functionality with persistent preferences
- **v0.1**: Initial release with session history sidebar

---

Built with philosophical wisdom and modern technology.
