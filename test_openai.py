import openai

openai.api_key = "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"

try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello world"}],
        max_tokens=5
    )
    print("API is working! Response:")
    print(response.choices[0].message.content.strip())
except Exception as e:
    print("Error calling OpenAI API:", e)
