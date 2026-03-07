import os
try:
    from google import genai
    client = genai.Client()
    video_file = client.files.upload(file='C:/Users/AD/.gemini/antigravity/brain/29b567a1-1706-4a1e-a339-89331ca56d15/npmjs_login_recording_1772866594500.webp')
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[
            video_file,
            "Describe the visual animation present in this image/video in detail, especially focusing on the UI login page animation.",
        ]
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
