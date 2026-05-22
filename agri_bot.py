import os

from huggingface_hub import InferenceClient

# Initialize the Hugging Face Inference Client.
# We explicitly target the fine-tuned agricultural model/provider.
MODEL_ID = "AI71ai/Llama-agrillm-3.3-70B:featherless-ai"

def _get_hf_token() -> str:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HF_token") or os.environ.get("hf_token")
    if not token:
        raise RuntimeError("HF_TOKEN is not set")
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
            "failed to resolve",
            "nameresolutionerror",
            "getaddrinfo failed",
            "max retries exceeded",
            "connection error",
            "connection refused",
            "timeout",
        )
    ):
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
