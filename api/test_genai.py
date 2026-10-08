import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')
print("Key exists:", bool(api_key))
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    resp = model.generate_content('test')
    print('GenAI Success!')
except Exception as e:
    import traceback
    traceback.print_exc()
