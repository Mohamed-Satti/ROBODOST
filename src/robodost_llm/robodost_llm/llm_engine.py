import os
from openai import OpenAI

class LlmEngine:
    def __init__(self, base_url="http://localhost:11434/v1", api_key="ollama", model_name=None):
        if model_name is None:
            model_name = os.getenv("ROBODOST_LLM_MODEL", "llama3.2:3B")
        """
        Initializes the LLM Engine using the standard OpenAI client.
        By default, it is configured for a local Ollama server.
        
        Args:
            base_url (str): The URL of the OpenAI-compatible API. 
                            (e.g., http://localhost:11434/v1 for Ollama)
            api_key (str): The API key. For Ollama, any string works.
            model_name (str): The name of the model to use.
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model_name = model_name
        self.history = []
        
        # System prompt defines the persona of the robot
        self.system_prompt = (
            "You are ROBODOST, a friendly and helpful AI robot assistant. "
            "Keep your answers extremely concise and conversational, as they will be spoken out loud via Text-to-Speech. "
            "Do not use markdown formatting, emojis, or lists. Speak naturally."
        )

    def generate(self, user_text):
        """
        Sends the user text to the LLM and returns the generated response.
        Maintains a short conversation history.
        """
        # Append user message to history
        self.history.append({"role": "user", "content": user_text})
        
        # Keep history short to save context window (e.g., last 5 interactions = 10 messages)
        if len(self.history) > 10:
            self.history = self.history[-10:]

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        try:
            print(f"[LLM] Sending to {self.model_name}...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=150  # Keep responses short for voice interactions
            )
            
            ai_text = response.choices[0].message.content.strip()
            
            # Append AI response to history
            self.history.append({"role": "assistant", "content": ai_text})
            
            return ai_text
            
        except Exception as e:
            print(f"[LLM] Error communicating with LLM: {e}")
            return "I'm sorry, I am having trouble connecting to my brain right now."

if __name__ == "__main__":
    # Simple test for the engine
    llm = LlmEngine()
    print("Testing local LLM (Make sure Ollama is running!)...")
    print("User: Hello!")
    print("Robot:", llm.generate("Hello!"))
