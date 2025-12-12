import os
from google import genai
from google.genai import types
from adk.agent import Agent, Message, Event

# The client automatically picks up the GOOGLE_API_KEY from the .env file
try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Google GenAI client. Ensure GOOGLE_API_KEY is set in your .env file: {e}")
    # You might want to exit or handle this more gracefully in a real app

# Define a function to generate content
def generate_response(prompt_text: str) -> str:
    if not client:
        return "API client not initialized."
        
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_text,
    )
    return response.text

# Define your ADK Agent logic
class MyAgent(Agent):
    def on_message(self, message: Message):
        """
        Handles incoming messages and generates a response using the Gemini API.
        """
        print(f"Received message: {message.text}")
        
        # Use the function defined above to interact with Google API
        ai_response = generate_response(message.text)
        
        # Send the AI-generated response back to the user/channel
        self.send(Message(text=ai_response))

# This part is usually provided by the ADK create template
if __name__ == "__main__":
    # The ADK framework handles the execution lifecycle
    pass
