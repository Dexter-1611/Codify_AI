import google.generativeai as genai

# Replace with your actual key
genai.configure(api_key="AIzaSyD6wnMAZvdCcEbvuvUX9gSJwqbjTxsv8SQ")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)