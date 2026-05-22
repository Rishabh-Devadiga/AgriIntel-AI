import os
import sys

from huggingface_hub import InferenceClient

# Initialize the Hugging Face Inference Client.
# We explicitly target the fine-tuned agricultural model/provider.
MODEL_ID = "AI71ai/Llama-agrillm-3.3-70B:featherless-ai"

TOKEN_ENV_NAMES = ("HF_TOKEN", "HF_token", "hf_token")

def _get_windows_user_env(name: str) -> str | None:
    """Read a user-level Windows environment variable without relying on process inheritance."""
    if sys.platform != "win32":
        return None

    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except OSError:
        return None

def _get_hf_token() -> str:
    token_candidates = []

    for name in TOKEN_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            token_candidates.append((f"process:{name}", value.strip()))

    for name in TOKEN_ENV_NAMES:
        value = _get_windows_user_env(name)
        if value:
            token_candidates.append((f"user:{name}", value.strip()))

    unique_tokens = {value for _, value in token_candidates if value}
    if not unique_tokens:
        raise RuntimeError("HF_TOKEN is not set")

    if len(unique_tokens) > 1:
        sources = ", ".join(source for source, _ in token_candidates)
        raise RuntimeError(
            "Multiple Hugging Face token environment variables are set with different values. "
            f"Clear the old token variables and keep only HF_TOKEN. Sources: {sources}"
        )

    token = unique_tokens.pop()
    return token

def _format_agri_llm_error(error: Exception) -> str:
    """Convert provider/client failures into safe user-facing chat messages."""
    message = str(error)
    message_lower = message.lower()

    if any(
        marker in message_lower
        for marker in (
            "hf_token",
            "keyerror",
            "is not set",
            "multiple hugging face token",
            "failed to resolve",
            "nameresolutionerror",
            "getaddrinfo failed",
            "max retries exceeded",
            "connection error",
            "connection refused",
            "timeout",
        )
    ):
        if "multiple hugging face token" in message_lower:
            return (
                "AgriLLM found multiple different Hugging Face tokens in the environment. "
                "Clear HF_TOKEN, HF_token, and hf_token, then set only HF_TOKEN to the new token."
            )

        if "hf_token" in message_lower or "keyerror" in message_lower:
            return "AgriLLM is not configured. Please set the HF_TOKEN environment variable and restart the app."

        return (
            "AgriLLM is currently unreachable. Please check your internet connection "
            "or DNS settings, then try again."
        )

    if "401" in message or "unauthorized" in message_lower or "invalid token" in message_lower:
        return "AgriLLM authentication failed. Please check the Hugging Face API token configuration."

    if "403" in message or "forbidden" in message_lower:
        return "AgriLLM access is not available for this account or model. Please verify model permissions."

    if "429" in message or "rate limit" in message_lower:
        return "AgriLLM is receiving too many requests right now. Please wait a moment and try again."

    if "503" in message or "currently loading" in message_lower or "model is loading" in message_lower:
        return "AgriLLM is warming up. Please try your question again in a minute."

    return "AgriLLM could not generate a response right now. Please try again shortly."

def ask_agriculture_expert(prompt: str) -> str:
    """
    Sends a query to the AgriLLM model and returns its response.
    """
    try:
        client = InferenceClient(api_key=_get_hf_token())

        # Structure the query using the chat completions API
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert agronomy assistant. Provide precise, actionable agricultural advice."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.7 # Lower value makes response more focused and factual
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return _format_agri_llm_error(e)

# Example Usage
if __name__ == "__main__":
    user_query = "What is the recommended crop rotation plan for corn fields experiencing high nitrogen depletion?"
    print(f"Querying AgriLLM: '{user_query}'...\n")
    
    answer = ask_agriculture_expert(user_query)
    print("--- AgriLLM Response ---")
    print(answer)
