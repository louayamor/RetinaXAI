from typing import Optional
from abc import ABC, abstractmethod

from loguru import logger


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass


class GitHubLLMClient(LLMClient):
    def __init__(self, token: str, model: str, endpoint: str = "https://models.github.ai/inference"):
        self.token = token
        self.model = model
        self.endpoint = endpoint
        self._client = None

    def _get_client(self):
        if self._client is None:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential
            self._client = ChatCompletionsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.token),
            )
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        from azure.ai.inference.models import SystemMessage, UserMessage

        messages = []
        if system_prompt:
            messages.append(SystemMessage(system_prompt))
        messages.append(UserMessage(prompt))

        response = self._get_client().complete(
            messages=messages,
            temperature=0.7,
            top_p=1.0,
            model=self.model
        )
        return response.choices[0].message.content


class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._get_client().chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content


class MockLLMClient(LLMClient):
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[Mock response for: {prompt[:50]}...]"


def get_llm_client(provider: str, **kwargs) -> LLMClient:
    providers = {
        "github": GitHubLLMClient,
        "openai": OpenAILLMClient,
        "mock": MockLLMClient,
    }

    client_class = providers.get(provider.lower(), MockLLMClient)
    logger.info(f"Initializing LLM client: {provider}")
    return client_class(**kwargs)
