

import requests
import json

# Replace 'your_api_key_here' with your actual OpenRouter API key
api_key = "..."

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "openai/gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": "Say hello."
        }
    ]
}

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    data=json.dumps(data)
)

print("Status Code:", response.status_code)

try:
    response_data = response.json()
    if "choices" in response_data:
        print("Assistant's Response:")
        print(response_data["choices"][0]["message"]["content"])
    elif "error" in response_data:
        print("API Error:")
        print(f"Code: {response_data['error'].get('code')}")
        print(f"Message: {response_data['error'].get('message')}")
    else:
        print("Unexpected response format:")
        print(json.dumps(response_data, indent=2))
except json.JSONDecodeError:
    print("Failed to parse JSON response:")
    print(response.text)