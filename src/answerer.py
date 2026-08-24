import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class Answerer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("WARNING: GEMINI_API_KEY is not set or is using the default value.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-3.6-flash'
        
    def generate_response(self, prompt, clauses=None):
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if clauses is not None:
                return self.fallback_response(clauses)
            return f"Error generating response: {e}"
            
    def fallback_response(self, clauses):
        return "REFUSAL\n\nI cannot answer this question from the policy manual.\n\nThe manual does not contain sufficient information to determine\nthe answer.\n\nNEXT STEP:\nRefer to a supervisor or appropriate program administrator."
