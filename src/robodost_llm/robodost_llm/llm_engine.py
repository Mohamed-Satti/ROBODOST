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
        self.set_language("auto")

    def set_language(self, language="auto"):
        base_prompt = (
            "You are ROBODOST, a friendly and helpful AI robot assistant. "
            "Keep your answers extremely concise and conversational, as they will be spoken out loud via Text-to-Speech. "
            "Do not use markdown formatting, emojis, or lists. Speak naturally."
        )
        if language == "tr":
            self.system_prompt = base_prompt + " IMPORTANT: Always respond strictly in Turkish."
        elif language == "en":
            self.system_prompt = base_prompt + " IMPORTANT: Always respond strictly in English."
        else:
            self.system_prompt = base_prompt + " IMPORTANT: Respond in the same language the user speaks."
        print(f"[LLM] Language set to: {language}")

    def set_model(self, model_name):
        self.model_name = model_name
        print(f"[LLM] Model set to: {self.model_name}")

    def get_available_models(self):
        """Fetches the list of installed models from Ollama."""
        try:
            models = self.client.models.list()
            return [m.id for m in models.data]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return [self.model_name]

    def generate_stream(self, user_text):
        """
        Sends the user text to the LLM and yields the response in sentences.
        Maintains a short conversation history.
        Filters out <think>...</think> blocks automatically.
        """
        import re
        self.history.append({"role": "user", "content": user_text})
        
        if len(self.history) > 10:
            self.history = self.history[-10:]

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        try:
            print(f"[LLM] Sending to {self.model_name} (Streaming)...")
            import time
            start_time = time.time()
            first_token_time = None
            token_count = 0

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500, # Increased to allow room for model thinking
                stream=True,
                extra_body={"options": {"num_ctx": 1024}} # Increased context slightly
            )
            
            full_text = ""
            buffer = ""
            sentence_buffer = ""
            in_think_block = False

            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    if first_token_time is None:
                        first_token_time = time.time()
                        ttft = first_token_time - start_time
                        print(f"\n[LLM Metrics] Time To First Token (TTFT): {ttft:.3f}s")
                        
                    token_count += 1
                    text_chunk = chunk.choices[0].delta.content
                    full_text += text_chunk
                    buffer += text_chunk
                    
                    if not in_think_block:
                        if "<think>" in buffer:
                            parts = buffer.split("<think>", 1)
                            sentence_buffer += parts[0]
                            buffer = parts[1]
                            in_think_block = True
                            
                    if in_think_block:
                        if "</think>" in buffer:
                            parts = buffer.split("</think>", 1)
                            buffer = parts[1]
                            in_think_block = False
                        else:
                            if len(buffer) > 10:
                                buffer = buffer[-10:]
                            continue
                            
                    if not in_think_block:
                        last_open = buffer.rfind('<')
                        if last_open != -1 and "<think>".startswith(buffer[last_open:]):
                            safe_text = buffer[:last_open]
                            buffer = buffer[last_open:]
                        else:
                            safe_text = buffer
                            buffer = ""
                            
                        sentence_buffer += safe_text
                        
                        # Yield when we hit a sentence boundary
                        matches = list(re.finditer(r'([.!?\n]+)', sentence_buffer))
                        if matches:
                            last_match = matches[-1]
                            split_point = last_match.end()
                            yield_text = sentence_buffer[:split_point].strip()
                            if yield_text:
                                yield yield_text
                            sentence_buffer = sentence_buffer[split_point:].lstrip()
            
            # Yield any remaining text
            if sentence_buffer.strip():
                yield sentence_buffer.strip()
                
            if first_token_time:
                end_time = time.time()
                generation_time = end_time - first_token_time
                if generation_time > 0:
                    tps = token_count / generation_time
                    print(f"\n[LLM Metrics] Speed (TPS): {tps:.1f} tokens/sec | Total Tokens: {token_count} | Total Time: {generation_time:.2f}s")
                
            self.history.append({"role": "assistant", "content": full_text.strip()})
            

        except Exception as e:
            print(f"[LLM] Error communicating with LLM: {e}")
            yield "I'm sorry, I am having trouble connecting to my brain right now."

    def generate(self, user_text):
        """
        Backwards compatible generate method that blocks until the stream is complete.
        """
        return " ".join(list(self.generate_stream(user_text)))

if __name__ == "__main__":
    # Simple test for the engine
    llm = LlmEngine()
    print("Testing local LLM (Make sure Ollama is running!)...")
    print("User: Hello!")
    print("Robot:", llm.generate("Hello!"))
