from openai import OpenAI
from config import OPENAI_API_KEY

# Initialize the OpenAI client
clientAI = OpenAI(api_key=OPENAI_API_KEY)

def generate_weather_advice(outdoor_temp, outdoor_weather):
    """Generate weather advice using GPT-3.5 based on the provided temperature and weather conditions."""
    prompt = (
        f"Today, the weather is {outdoor_weather} with a temperature of {outdoor_temp}°C. "
        "Tell how much degrees it is and the outside weather. Give some advice before going outside."
    )

    chat_completion = clientAI.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
        max_tokens=90,
        temperature=0.7
    )

    advice = chat_completion.choices[0].message.content.strip()
    return advice
