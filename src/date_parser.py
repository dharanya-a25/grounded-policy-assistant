import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
import re

class DateParser:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
        
    def extract_claim_date(self, question):
        prompt = f"""
You are a date extraction assistant.
Extract the "claim date" from the following question if one is mentioned.
Return the date in YYYY-MM-DD format if it is an exact date.
If only a month and year are given, use the first of the month (e.g., February 2026 -> 2026-02-01).
If no claim date is mentioned, return exactly: NONE

Question: {question}

Format your response as just the date or NONE. No other text.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip().upper()
            if text == "NONE":
                return None
            
            match = re.search(r'\d{4}-\d{2}-\d{2}', text)
            if match:
                return match.group(0)
            return None
        except Exception as e:
            return self.regex_fallback(question)

    def regex_fallback(self, question):
        # Deterministic fallback if API fails
        months = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04', 
            'may': '05', 'june': '06', 'july': '07', 'august': '08', 
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        q_lower = question.lower()
        
        # Match "1 March 2026" or "March 1, 2026"
        for m, m_num in months.items():
            # Pattern: 1 March 2026
            p1 = rf'(\d{{1,2}})\s+{m}\s+(\d{{4}})'
            match = re.search(p1, q_lower)
            if match:
                day = match.group(1).zfill(2)
                year = match.group(2)
                return f"{year}-{m_num}-{day}"
                
            # Pattern: March 1, 2026 or March 1 2026
            p2 = rf'{m}\s+(\d{{1,2}})[,\s]+(\d{{4}})'
            match = re.search(p2, q_lower)
            if match:
                day = match.group(1).zfill(2)
                year = match.group(2)
                return f"{year}-{m_num}-{day}"
                
            # Pattern: March 2026 (assume 1st)
            p3 = rf'{m}\s+(\d{{4}})'
            match = re.search(p3, q_lower)
            if match:
                year = match.group(1)
                return f"{year}-{m_num}-01"
                
        return None
