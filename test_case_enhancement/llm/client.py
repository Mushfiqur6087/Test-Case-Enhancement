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

import base64
import litellm  # type: ignore
from typing import Optional

# Silently drop unsupported params per model/provider (e.g. temperature on
# o-series reasoning models). This is the clean, provider-agnostic solution.
litellm.drop_params = True

# Known vision-capable model name fragments. If the configured model matches
# any of these substrings, screenshots will be attached to checker calls.
_VISION_MODEL_FRAGMENTS = (
    "gpt-4o",
    "gpt-5",
    "gpt-4-turbo",
    "claude-3",
    "gemini",
    "vision",
)


def _is_vision_model(model_name: str) -> bool:
    """Return True if the model is known to support image inputs."""
    lower = model_name.lower()
    return any(fragment in lower for fragment in _VISION_MODEL_FRAGMENTS)


class LLMClient:
    """LLMClient class."""
    def __init__(
        self,
        api_key: str,
        model_name: str = "openai/gpt-4o-mini",
        system_prompt: str = "You are a helpful assistant.",
        debug_file: str = None,
    ):
        """Initialize the __init__ method."""
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.debug_file = debug_file
        self._call_count = 0
        self._system_prompt_logged = False
        self.supports_vision: bool = _is_vision_model(model_name)

    def ask(self, user_prompt: str) -> str:
        """Send a text-only prompt to the model via LiteLLM."""
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

    def ask_with_screenshot(
        self,
        user_prompt: str,
        screenshot_b64: str,
        mime_type: str = "image/png",
    ) -> str:
        """Send a prompt with an attached screenshot (vision call).

        If the model doesn't support vision or the call fails for any image-
        related reason, falls back to plain text ask() automatically.

        Parameters
        ----------
        user_prompt   : text portion of the prompt
        screenshot_b64: base64-encoded screenshot bytes
        mime_type     : MIME type of the image (default: image/png)
        """
        if not self.supports_vision or not screenshot_b64:
            return self.ask(user_prompt)

        self._call_count += 1
        call_num = self._call_count

        user_content = [
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{screenshot_b64}",
                    "detail": "high",
                },
            },
        ]

        try:
            response = litellm.completion(
                model=self.model_name,
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
                num_retries=2,
                timeout=180,   # vision calls can be slower
            )
            result = response.choices[0].message.content

            if self.debug_file:
                self._log_llm_call(
                    call_num,
                    f"[VISION] {user_prompt[:200]}... + screenshot ({len(screenshot_b64)} b64 chars)",
                    result,
                )
            return result

        except Exception as e:
            # If vision fails (unsupported, rate limit, etc.) fall back to text
            if self.debug_file:
                self._log_llm_call(
                    call_num,
                    f"[VISION→TEXT fallback, reason: {e}] {user_prompt[:200]}...",
                    "(falling back to text-only)",
                )
            return self.ask(user_prompt)

    @property
    def is_vision(self) -> bool:
        """True if this client's model supports image inputs."""
        return self.supports_vision

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
