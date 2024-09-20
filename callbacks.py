import streamlit as st
from groq import Groq, GroqError
import os

def on_click_callback(context):
    system_prompt = """
    You are HealthAdviser, a chatbot designed to provide personalized health advice. 
    Your primary goal is to answer user queries related to health. 
    Ensure privacy by obfuscating sensitive information. 
    Minimize the amount of user input needed unless highly probable that additional information will improve the advice.
    Consider age, weight, height, region of the world for epidemiological reasons, and biological heritage (e.g., Caucasian, Asian) when giving health advice.
    No need for a full medical profile unless required for specific health and well-being management.
    Ensure ease of use to avoid annoying the users.
    Dont ask for question if you dont need any information from user.
    """

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("Groq API key not found. Please set the GROQ_API_KEY environment variable.")
        return ""

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        response_text = ""
        for chunk in completion:
            response_text += chunk.choices[0].delta.content or ""

        return response_text

    except GroqError as e:
        st.error(f"Groq API error: {e}")
        return ""
