"""
Hack code to support anthropic and make it looks like openai
"""
import logging

try:
    from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
except:
    logging.warning("anthropic not supported, pip install anthropic")
import json
from time import time


def format_for_chat_completion(prompt):
    if isinstance(prompt, str):
        payload = f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}"
    elif isinstance(prompt, list) and isinstance(prompt[0], str):
        messages = []
        idx = 0
        for idx, p in enumerate(prompt):
            prefix = HUMAN_PROMPT if idx % 2 == 0 else AI_PROMPT
            messages.append(f"{prefix} {p}")
        last_idx = idx + 1
        postfix = AI_PROMPT if last_idx % 2 == 0 else HUMAN_PROMPT
        payload = " ".join(messages) + " " + postfix
    return payload


class ClaudeCompletion:
    def __init__(
        self,
        api_key,
    ) -> None:
        self.api_key = api_key
        self.anthropic = Anthropic(api_key=api_key)

    def completion(
        self,
        prompt,
        model_name="claude-1.3",
        temperature=0.7,
        max_tokens=2048,
        top_p=0,
        top_k=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["<|im_end|>"],
    ):
        prompt = format_for_chat_completion(prompt)
        start = time()
        completion = self.anthropic.completions.create(
            model=model_name,
            prompt=prompt,
            max_tokens_to_sample=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop,
        )
        elapsed = time() - start
        completed_txt = completion.completion.lstrip()
        response = {
            "model": model_name,
            "choices": [
                {
                    "message": {"role": "assistant", "content": completed_txt},
                    "finish_reason": completion.stop_reason,
                }
            ],
            "elapsed": elapsed,
        }
        return completed_txt, response
