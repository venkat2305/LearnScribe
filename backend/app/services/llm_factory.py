from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI as OpenRouterChatOpenAI
from typing import Dict, Any
from app.config import config


def get_llm_client(model_config: Dict[str, Any]):
    provider = model_config.get("provider")
    config_params = model_config.get("config", {})
    print(f"LLM provider: {provider}")
    print(f"LLM config params: {config_params}")

    if provider == "groq":
        config_params["groq_api_key"] = config.GROQ_API_KEY
        return ChatGroq(**config_params)

    elif provider == "gemini":
        config_params["google_api_key"] = config.GOOGLE_GEMINI_KEY
        return ChatGoogleGenerativeAI(**config_params)

    elif provider == "openrouter":
        config_params["openai_api_key"] = config.OPEN_ROUTER_KEY
        config_params.setdefault("model_kwargs", {}).setdefault("headers", {
            "HTTP-Referer": config_params.get("your_site_url"),
            "X-Title": config_params.get("your_site_name"),
        })
        return OpenRouterChatOpenAI(**config_params)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
