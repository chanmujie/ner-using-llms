import json
import time
import re
import urllib.request
import os
import ssl
from pathlib import Path
from typing import Dict, Any, List, Union
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

class Llama:
    """
    Class for interacting with Llama 3.1 8b Instruct API
    """
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self._setup_ssl()
        
    def _setup_ssl(self, allowed: bool = True):
        """Bypass SSL verification if needed (for testing only)"""
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context
    
    def create_message(self, system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
        """Create a properly formatted message for the API"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    def generate_completion(self, system_prompt: str, user_prompt: str) -> bytes:
        """Generate completion from the LLM API"""
        messages = self.create_message(system_prompt, user_prompt)
        
        data = {
            "input_data": {
                "input_string": messages,
                "parameters": {
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "min_p": 0.1,
                    "max_new_tokens": 4000
                }
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(data).encode('utf-8'),
            headers=headers
        )
        try:
            start_time = time.time()
            with urllib.request.urlopen(req) as response:
                result = response.read()
            latency = time.time() - start_time
            return result, latency
        except urllib.error.HTTPError as error:
            error_content = error.read().decode("utf8", 'ignore')
            raise Exception(
                f"API request failed with status {error.code}\n"
                f"Headers: {dict(error.info())}\n"
                f"Response: {error_content}"
            )
        
class Phi:
    """
    Class for interacting with Phi 4 Reasoning Model (Azure AI Studio).
    """
    def __init__(self, endpoint: str, api_key: str, model_name: str = "phi-4-reasoning"):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_name = model_name

        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
            model=self.model_name
        )

    def format_phi_chatml(self, system_prompt: str, user_prompt: str) -> list:
        """Formats the prompts according to Phi-4's requirements.
        
        Args:
            system_prompt: The full system prompt from Phi-4's documentation
            user_prompt: The actual prompt with input text to process
        
        Returns:
            List of message dictionaries for ChatCompletions API
        """
        system = """
    You are Phi, a language model trained by Microsoft to help users. Your role as an assistant involves thoroughly exploring questions through a systematic thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered thinking process. Please structure your response into two main sections: Thought and Solution using the specified format: <think> {Thought section} </think> {Solution section}. In the Thought section, detail your reasoning process in steps. Each step should include detailed considerations such as analysing tasks, summarizing relevant findings, brainstorming new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. In the Solution section, based on various attempts, explorations, and reflections from the Thought section, systematically present the final solution that you deem correct. The Solution section should be logical, accurate, and concise and detail necessary steps needed to reach the conclusion. Now, try to solve the following task through the above guidelines:
        """
        # Insert user_prompt into the template (which becomes the system message)
        populated_user_prompt = system_prompt.format(user_input=user_prompt)
        return [
            SystemMessage(content=system),
            UserMessage(content=populated_user_prompt)
        ]

    def generate_completion(self, system_prompt: str, user_prompt: str) -> tuple[str, float]:
        """Send request to Phi model and return (clean text, latency in sec)"""
        messages = self.format_phi_chatml(system_prompt, user_prompt)
        
        start_time = time.time()
        response = self.client.complete(
            messages=messages,
            max_tokens=8000,
            temperature=0.3,
            top_p=1,
            response_format="text"
        )
        latency = time.time() - start_time

        # Extract content safely from response
        raw_content = response.choices[0].message.content

        ## Remove <think> ... </think> blocks
        # clean_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()

        return raw_content, latency
    
class Extractor:
    """
    Class for processing LLM outputs and extracting structured data.
    Assumes each extracted item includes an "input" field for matching.
    """

    @staticmethod
    def parse_response(response: Union[bytes, str]) -> Any:
        """Parse API response (bytes or str) and extract JSON list or single object"""
        if isinstance(response, bytes):
            response_str = response.decode("utf-8")
        else:
            response_str = response

        try:
            wrapper = json.loads(response_str)
            content = wrapper.get('output', '')
        except json.JSONDecodeError:
            content = response_str

        patterns = [
            r'```json\n(.*?)\n```',      # match *any* JSON inside fences
            r'```\n(.*?)\n```',
            r'({.*?})',                  # raw JSON object
            r'(\[.*?\])'                 # raw JSON array
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        raise ValueError(f"No valid JSON found in response:\n{content[:500]}...")

    @staticmethod
    def parse_entities_from_extracted(extracted: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Convert batched extracted list into a mapping: input_text → list of entity dicts
        Each extracted item should have:
        {
            "input": "original input string",
            "<entity_type>": [...]
        }
        """
        if isinstance(extracted, dict):
            extracted = [extracted]  # treat single object as one-item list

        entity_map = {}

        for item in extracted:
            input_text = item.get("input", "").strip()
            if not input_text:
                continue

            all_entities = []
            for label, value in item.items():
                if label == "input":
                    continue

                if isinstance(value, list):
                    for v in value:
                        if label in ["name", "organisation", "email", "phone_number"]:
                            key_map = {
                                "name": "name",
                                "organisation": "name",
                                "email": "email",
                                "phone_number": "number"
                            }
                            clean_text = v.get(key_map[label], "").strip()
                        else:
                            clean_text = v.get(label, "").strip()

                        if clean_text and clean_text.lower() != "null":
                            extra_fields = {k: v[k] for k in v if k not in {label, "name", "email", "number"}}
                            all_entities.append({
                                "label": label,
                                "clean_text": clean_text,
                                "extra_fields": extra_fields
                            })

            entity_map[input_text] = all_entities

        return entity_map

    @staticmethod
    def save_to_file(data: Union[Dict, List], filename: str = "output.json"):
        """Save extracted data to a JSON file"""
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_path
    
