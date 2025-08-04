import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr


def model() -> BaseChatModel:
    model_name = os.getenv("MODEL")
    model_provider = os.getenv("MODEL_PROVIDER")
    print(f"Initializing LLM with model: {model_name} and provider: {model_provider}\n")

    llm = init_chat_model(model=model_name, model_provider=model_provider,
                          api_key=SecretStr(os.getenv("GOOGLE_API_KEY")))

    return llm
