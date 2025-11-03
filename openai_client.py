import os
import openai

# Get your API key from environment variables for safety
openai.api_key = os.getenv("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")

def ask_gpt4_turbo(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"OpenAI API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

if __name__ == "__main__":
    prompt = "Explain the concept of immortality."
    print("GPT-4 Turbo says:", ask_gpt4_turbo(prompt))
