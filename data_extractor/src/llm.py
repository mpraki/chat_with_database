import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

_llm_instance = None


def model() -> BaseChatModel:
    global _llm_instance
    if _llm_instance is None:
        model_name = os.getenv("MODEL")
        model_provider = os.getenv("MODEL_PROVIDER")
        api_key_env = os.getenv("MODEL_PROVIDER_API_KEY_NAME")
        api_key = os.getenv(api_key_env)

        print(f"Initializing LLM with model: {model_name}, provider: {model_provider}, api_key_env: {api_key_env}\n")
        _llm_instance = init_chat_model(model=model_name, model_provider=model_provider,
                                        api_key=SecretStr(api_key))
    return _llm_instance
