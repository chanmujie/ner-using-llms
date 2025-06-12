from typing import List
import keyring
from openai import AzureOpenAI

# --- Set up Azure OpenAI client ---
endpoint = keyring.get_password("azure-openai", "endpoint")
subscription_key = keyring.get_password("azure-openai", "api_key")
api_version = "{version}"
deployment = "gpt-4o"

client = AzureOpenAI(
    api_key=subscription_key,
    api_version=api_version,
    azure_endpoint=endpoint,
)

# --- Base generator function ---

def generate_entities(prompt: str) -> List[str]:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a synthetic data generation assistant trained to return JSONL-formatted lines for synthetic data. No commentary or previews."

            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=3000,
        temperature=0.7,
        top_p=1.0
    )

    output_text = response.choices[0].message.content
    return [line.strip() for line in output_text.strip().splitlines() if line.strip()]