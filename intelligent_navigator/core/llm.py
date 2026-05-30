"""LLM client wrapper using LiteLLM for unified provider routing.

Drop-in for any OpenAI-compatible or other provider.
Model strings follow LiteLLM convention:
    openai/gpt-5-mini
    openai/gpt-4o-mini
    anthropic/claude-3-5-sonnet-20241022
    openrouter/anthropic/claude-3.5-sonnet
    github/gpt-4o

``litellm.drop_params = True`` silently removes any parameter a model doesn't
support (e.g. temperature on reasoning models) — no manual detection needed.
"""

import litellm  # type: ignore
from typing import Optional

# Silently drop unsupported params per model/provider (e.g. temperature on
# o-series reasoning models). This is the clean, provider-agnostic solution.
litellm.drop_params = True


class LLMClient:
    def __init__(
        self,
        api_key: str,
        model_name: str = "openai/gpt-4o-mini",
        system_prompt: str = "You are a helpful assistant.",
        debug_file: str = None,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.debug_file = debug_file
        self._call_count = 0
        self._system_prompt_logged = False

    def ask(self, user_prompt: str) -> str:
        """Send a prompt to the model via LiteLLM and return the response."""
        self._call_count += 1
        call_num = self._call_count

        response = litellm.completion(
            model=self.model_name,
            api_key=self.api_key,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,   # dropped automatically for models that reject it
            num_retries=2,
            timeout=120,
        )
        result = response.choices[0].message.content

        if self.debug_file:
            self._log_llm_call(call_num, user_prompt, result)

        return result

    def set_debug_file(self, debug_file: str) -> None:
        """Set or update the debug file path."""
        self.debug_file = debug_file
        self._system_prompt_logged = False

    def _log_llm_call(self, call_num: int, user_prompt: str, response: str) -> None:
        """Write full LLM interaction to debug file."""
        try:
            with open(self.debug_file, "a", encoding="utf-8") as f:
                f.write("\n")
                f.write("=" * 60 + "\n")
                f.write(f"LLM CALL #{call_num}  [model: {self.model_name}]\n")
                f.write("=" * 60 + "\n")

                if not self._system_prompt_logged:
                    f.write("\n--- SYSTEM PROMPT ---\n")
                    f.write(self.system_prompt.strip())
                    f.write("\n")
                    self._system_prompt_logged = True

                f.write("\n--- USER PROMPT ---\n")
                f.write(user_prompt.strip())
                f.write("\n")

                f.write("\n--- RESPONSE ---\n")
                f.write(response.strip() if response else "(empty)")
                f.write("\n")
                f.write("=" * 60 + "\n")
        except Exception:
            pass
