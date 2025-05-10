import streamlit as st
import pandas as pd
import requests
import os

# Optional: If not using st.secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
 # or os.getenv("GROQ_API_KEY")

st.title(" GenAI Persona & Campaign Generator (Powered by Groq)")

st.sidebar.header("🧍 Customer Profile")
name = st.sidebar.text_input("Name", "Jane")
age = st.sidebar.slider("Age", 18, 70, 32)
income = st.sidebar.number_input("Monthly Income (₦)", 50000, 5000000, 1200000, step=50000)
profession = st.sidebar.text_input("Profession", "Freelancer")
interests = st.sidebar.text_area("Interests (comma-separated)", "saving, side hustle, tech gadgets")
risk_tolerance = st.sidebar.selectbox("Risk Tolerance", ["Low", "Moderate", "High"])

if st.sidebar.button("🎯 Generate with Groq LLM"):
    user_profile = f"""
    Name: {name}
    Age: {age}
    Income: ₦{income:,}
    Profession: {profession}
    Interests: {interests}
    Risk Tolerance: {risk_tolerance}
    """

    prompt = f"""
    You are a fintech-focused marketing AI. Based on the customer profile below, generate:
    1. A short and realistic marketing persona description.
    2. A personalized fintech marketing message (friendly tone) promoting a savings or investment product.

    Customer Profile:
    {user_profile}

    Respond in this format:
    Persona:
    <description>

    Campaign Message:
    <message>
    """

    with st.spinner("💡 Generating with Groq..."):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistral-saba-24b",
            "messages": [
                {"role": "system", "content": "You are an expert marketing assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        result = response.json()

        # Check if 'choices' exists

        if 'choices' in result:
            ai_output = result['choices'][0]['message']['content']
            
            # Split response
            parts = ai_output.split("Campaign Message:")
            persona = parts[0].replace("Persona:", "").strip()
            message = parts[1].strip() if len(parts) > 1 else "N/A"

            st.subheader("🧬 AI-Generated Persona")
            st.write(persona)

            st.subheader("💬 Campaign Message")
            st.info(message)

            # CSV export
            output = pd.DataFrame({
                "Name": [name],
                "Age": [age],
                "Profession": [profession],
                "Income": [income],
                "Interests": [interests],
                "Risk Tolerance": [risk_tolerance],
                "Persona": [persona],
                "Message": [message]
            })
            csv = output.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Result", csv, f"{name}_groq_campaign.csv", "text/csv")

        else:
            st.error("❌ Groq API did not return a valid response.")
            st.json(result)  # Display the actual error response



