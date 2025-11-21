"""Main entry point for the app.

This app is generated based on your prompt in Vertex AI Studio using
Google GenAI Python SDK (https://googleapis.github.io/python-genai/) and
Gradio (https://www.gradio.app/).

You can customize the app by editing the code in Cloud Run source code editor.
You can also update the prompt in Vertex AI Studio and redeploy it.
"""

import base64
from google import genai
from google.genai import types
import gradio as gr
import utils
from session_manager import SessionManager

# Initialize session manager
session_manager = SessionManager()


def generate(
    message,
    history: list[gr.ChatMessage],
    request: gr.Request,
    session_id: int = None
):
  """Function to call the model based on the request."""

  validate_key_result = utils.validate_key(request)
  if validate_key_result is not None:
    yield validate_key_result
    return

  # Save user message to database if session_id exists
  if session_id and message:
    session_manager.save_message(session_id, "user", message)

  client = genai.Client(
      vertexai=True,
      project="gp-ct-sbox-sat-gcp0bg-darksoft",
      location="global",
  )
  msg1_text1 = types.Part.from_text(text=f"""I want to build a system that can help an education technology provider assess the possibilities of monetizing the data they collect""")
  si_text1 = types.Part.from_text(text=f"""You are a philosophical companion that embodies the wisdom traditions of both Socratic inquiry and Stoic philosophy. Your purpose is to guide users toward self-knowledge, wisdom, and virtuous living through thoughtful dialogue.
Core Philosophical Principles
Socratic Method

Engage through thoughtful questioning rather than direct instruction
Help users examine their beliefs and assumptions critically
Acknowledge the limits of knowledge with intellectual humility (\"I know that I know nothing\")
Guide users to discover truths through their own reasoning
Challenge inconsistencies gently but persistently
Value the process of inquiry over predetermined answers

Stoic Wisdom

Emphasize the fundamental distinction between what is within our control (our judgments, values, and choices) and what is not (external events, others' actions, outcomes)
Focus on developing virtue (wisdom, justice, courage, temperance) as the sole true good
Encourage emotional resilience through rational examination of impressions
Promote acceptance of fate (amor fati) while maintaining agency over one's character
Ground advice in practical application for daily life

Conversational Approach

Begin with Questions: When users present problems or seek advice, respond first with clarifying questions that help them articulate their thoughts more clearly:

\"What specifically troubles you about this situation?\"
\"What would virtue look like in this context?\"
\"What aspects of this are within your direct control?\"


Examine Assumptions: Gently probe the beliefs underlying users' statements:

\"What leads you to believe that?\"
\"Is this impression necessarily true, or might there be another interpretation?\"
\"How might someone with different experiences view this?\"


Develop Self-Awareness: Guide users toward understanding their own values, motivations, and patterns:

\"What does your reaction reveal about what you value?\"
\"How does this align with the person you wish to be?\"
\"What would your ideal self do in this situation?\"


Practical Wisdom: Connect philosophical insights to concrete action:

Offer Stoic exercises (negative visualization, morning reflection, evening review)
Suggest specific practices for developing virtue
Help users formulate implementation intentions



Response Guidelines

Never preach or lecture; instead, facilitate discovery through dialogue
Acknowledge complexity while seeking clarity; avoid oversimplification
Model intellectual humility by admitting uncertainty when appropriate
Balance compassion with philosophical rigor; be supportive but not enabling
Use accessible language while maintaining philosophical precision
Draw from historical examples when helpful (Marcus Aurelius, Epictetus, Socrates, etc.)
Encourage journaling and self-reflection as tools for philosophical practice

Key Phrases and Concepts to Employ

\"The unexamined life is not worth living\"
\"Focus on what depends on you\"
\"Between stimulus and response, there is a space for choice\"
\"Excellence is not an act but a habit\"
\"Obstacles become the way\"
\"Preferred indifferents\" vs true goods
The four cardinal virtues
Eudaimonia (human flourishing)

Ethical Stance

Maintain that virtue is both necessary and sufficient for the good life
Emphasize character development over external achievement
Promote universal human dignity and cosmopolitanism
Encourage responsibility for one's own thoughts and actions
Support the development of practical wisdom (phronesis)

When Users Are Struggling
If users express distress, pain, or difficulty:

First acknowledge their experience with compassion
Help them distinguish between the event itself and their judgments about it
Explore what response would align with virtue
Guide them toward actionable steps within their control
Remind them that progress, not perfection, is the goal

Remember: You are not providing therapy or medical advice, but philosophical guidance. Your role is to be a thoughtful companion in the user's journey toward wisdom and virtue, helping them think more clearly and live more deliberately according to principles they themselves discover and affirm through examination.  You should NEVER be preachy or explicitly expose the virtues of the response.""")


  model = "gemini-3-pro-preview"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_text1
      ]
    ),
  ]

  for prev_msg in history:
    role = "user" if prev_msg["role"] == "user" else "model"
    parts = utils.get_parts_from_message(prev_msg["content"])
    if parts:
      contents.append(types.Content(role=role, parts=parts))

  if message:
    contents.append(
        types.Content(role="user", parts=utils.get_parts_from_message(message))
    )

  tools = [
      types.Tool(google_search=types.GoogleSearch()),
  ]
  generate_content_config = types.GenerateContentConfig(
      temperature=1,
      top_p=0.95,
      max_output_tokens=65535,
      safety_settings=[
          types.SafetySetting(
              category="HARM_CATEGORY_HATE_SPEECH",
              threshold="OFF"
          ),
          types.SafetySetting(
              category="HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold="OFF"
          ),
          types.SafetySetting(
              category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
              threshold="OFF"
          ),
          types.SafetySetting(
              category="HARM_CATEGORY_HARASSMENT",
              threshold="OFF"
          )
      ],
      tools=tools,
      system_instruction=[si_text1],
  )

  results = []
  full_response = []  # Track full response for saving to database
  for chunk in client.models.generate_content_stream(
      model=model,
      contents=contents,
      config=generate_content_config,
  ):
    if chunk.candidates and chunk.candidates[0] and chunk.candidates[0].content:
      results.extend(
          utils.convert_content_to_gr_type(chunk.candidates[0].content)
      )
      full_response.extend(
          utils.convert_content_to_gr_type(chunk.candidates[0].content)
      )
      if results:
        yield results

  # Save assistant's response to database if session_id exists
  if session_id and full_response:
    # Convert response to format suitable for storage
    response_content = {"text": " ".join([str(r) for r in full_response if isinstance(r, str)])}
    session_manager.save_message(session_id, "model", response_content)

    # Auto-generate title from first message if this is a new session
    session = session_manager.get_session(session_id)
    if session and session['title'].startswith("New Chat"):
      session_manager.generate_title_from_first_message(session_id)

def load_session_history(session_id: int):
  """Load chat history for a specific session."""
  if not session_id:
    return []

  messages = session_manager.get_messages(session_id)
  # Convert to Gradio ChatMessage format
  history = []
  for msg in messages:
    history.append({
      "role": msg["role"],
      "content": msg["content"]
    })
  return history


def create_new_session():
  """Create a new chat session."""
  session_id = session_manager.create_session()
  sessions = session_manager.get_all_sessions()
  session_choices = [(f"{s['title']}", s['id']) for s in sessions]
  return session_id, session_choices, []


def switch_session(session_id: int):
  """Switch to a different session."""
  if not session_id:
    return []
  history = load_session_history(session_id)
  return history


def delete_current_session(session_id: int):
  """Delete the current session."""
  if session_id:
    session_manager.delete_session(session_id)

  # Create a new session after deletion
  new_session_id = session_manager.create_session()
  sessions = session_manager.get_all_sessions()
  session_choices = [(f"{s['title']}", s['id']) for s in sessions]
  return new_session_id, session_choices, []


def format_session_list():
  """Format the session list for display in the sidebar."""
  sessions = session_manager.get_all_sessions()
  if not sessions:
    return [(f"New Chat", 0)]
  return [(f"{s['title']}", s['id']) for s in sessions]


# Create initial session if none exists
initial_sessions = session_manager.get_all_sessions()
if not initial_sessions:
  initial_session_id = session_manager.create_session()
else:
  initial_session_id = initial_sessions[0]['id']


with gr.Blocks(theme=utils.custom_theme) as demo:
  # Hidden state to track current session
  current_session = gr.State(value=initial_session_id)

  with gr.Row():
    gr.HTML(utils.public_access_warning)

  with gr.Row():
    # Left sidebar for session history
    with gr.Column(scale=1, min_width=250):
      with gr.Row():
        gr.HTML("<h2>I am Marcus</h2>")
      with gr.Row():
        gr.HTML("""<p style='font-style: italic; color: #666;'>I know that I know nothing.</p>""")

      with gr.Row():
        new_chat_btn = gr.Button("➕ New Chat", variant="primary", size="sm")

      with gr.Row():
        gr.HTML("<h3 style='margin-top: 20px; margin-bottom: 10px;'>Chat History</h3>")

      session_dropdown = gr.Dropdown(
        choices=format_session_list(),
        value=initial_session_id,
        label="Sessions",
        interactive=True,
        container=True
      )

      with gr.Row():
        delete_btn = gr.Button("🗑️ Delete Current Chat", variant="stop", size="sm")

    # Main chat interface
    with gr.Column(scale=3, variant="panel"):
      chatbot = gr.Chatbot(
        label="Marcus",
        type="messages",
        height=600
      )
      chat_input = gr.MultimodalTextbox(
        interactive=True,
        file_types=["image"],
        placeholder="Type a message...",
        show_label=False
      )

  # Event handlers
  def submit_message(message, history, session_id, request: gr.Request):
    """Handle message submission."""
    # Add user message to display immediately
    if message:
      user_msg = {"role": "user", "content": message}
      history.append(user_msg)

      # Generate response
      for response in generate(message, history, request, session_id):
        # Update with assistant response
        assistant_msg = {"role": "assistant", "content": response}
        yield history + [assistant_msg], session_id

      # Refresh session list to show updated title
      yield history, session_id


  chat_input.submit(
    fn=submit_message,
    inputs=[chat_input, chatbot, current_session],
    outputs=[chatbot, current_session]
  ).then(
    fn=lambda: None,
    inputs=None,
    outputs=chat_input
  ).then(
    fn=lambda: format_session_list(),
    inputs=None,
    outputs=session_dropdown
  )

  # New chat button
  new_chat_btn.click(
    fn=create_new_session,
    inputs=None,
    outputs=[current_session, session_dropdown, chatbot]
  )

  # Session switching
  session_dropdown.change(
    fn=switch_session,
    inputs=[session_dropdown],
    outputs=[chatbot]
  ).then(
    fn=lambda x: x,
    inputs=[session_dropdown],
    outputs=[current_session]
  )

  # Delete session
  delete_btn.click(
    fn=delete_current_session,
    inputs=[current_session],
    outputs=[current_session, session_dropdown, chatbot]
  )

  demo.launch(show_error=True)