from functools import cache

from openrouter import OpenRouter

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


@cache
def get_client() -> OpenRouter:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set (add it to .env)")
    return OpenRouter(api_key=OPENROUTER_API_KEY)


def complete(
    prompt: str,
    *,
    system: str | None = None,
    model: str = OPENROUTER_MODEL,
    temperature: float = 0.0,
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = get_client().chat.send(
        model=model,
        messages=messages,
        temperature=temperature,
        provider={"sort": "price"},
    )
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    print(complete("Say hello in one short sentence."))
