"""
Hack code to support both openai platform and azure dedicated pricing
"""
import openai
import requests
import json
from time import time


def format_for_chat_completion(prompt):
    if isinstance(prompt, str):
        payload = {"messages": [{"role": "user", "content": prompt}]}
    elif isinstance(prompt, list) and isinstance(prompt[0], str):
        messages = [
            {"role": "user" if idx % 2 == 0 else "assistant", "content": p}
            for idx, p in enumerate(prompt)
        ]
        payload = {"messages": messages}
    elif isinstance(prompt, list) and isinstance(prompt[0], dict):
        payload = {"messages": prompt}
    return payload["messages"]


class OpenAICompletion:
    def __init__(
        self,
        api_key,
        azure_api_key=None,
        azure_api_version=None,
        azure_backend_url=None,
        azure_model_remap={
            "gpt-3.5-turbo": "turbo_35",
            "gpt-4": "gpt_4",
            "gpt-4-32k": "gpt_4_32k",
        },
    ) -> None:
        self.api_key = api_key
        self.azure_backend_enabled = False
        self.azure_model_remap = azure_model_remap
        if azure_api_key and azure_api_version and azure_backend_url:
            self.azure_backend_enabled = True
            self.azure_api_key = azure_api_key
            self.azure_api_version = azure_api_version
            self.azure_backend_url = azure_backend_url

    def setup_azure(self):
        assert self.azure_backend_enabled
        openai.api_type = "azure"
        openai.api_version = self.azure_api_version
        openai.api_base = self.azure_backend_url
        openai.api_key = self.azure_api_key

    def setup_openai(self):
        openai.api_type = "open_ai"
        openai.api_version = None
        openai.api_base = "https://api.openai.com/v1"
        openai.api_key = self.api_key

    def completion(self, *args, **kwargs):
        if self.azure_backend_enabled:
            res = self.azure_completion(*args, **kwargs)
        res = self.openai_completion(*args, **kwargs)
        return res["choices"][0]["message"]["content"], res

    def openai_completion(
        self,
        prompt,
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=2048,
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["<|im_end|>"],
    ):
        """
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content":<response>,
                "role": "assistant"
            }
        }
        """
        self.setup_openai()
        success = False
        while not success:
            try:
                start = time()
                response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=format_for_chat_completion(prompt),
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop,
                )

                # response = chatbot.ask(row['question'])
                elapsed = time() - start
                success = True
            except Exception as e:
                print("fallback", e)
                continue
        return response

    def azure_completion(
        self,
        prompt,
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=2048,
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["<|im_end|>"],
        use_openai=False,
    ):
        """
        {
            "finish_reason": "stop",
            "index": 0,
            "text": <response text>,
            "elapsed": <seconds to finish>
        }
        """
        success = False

        self.setup_azure()

        while not success:
            try:
                if use_openai:
                    raise ValueError("Azure OpenAI’s content management policy")
                deployment_name = self.azure_model_remap[model_name]
                url = (
                    openai.api_base
                    + "/openai/deployments/"
                    + deployment_name
                    + "/chat/completions"
                )
                payload = {
                    "messages": format_for_chat_completion(prompt),
                    "stop": stop,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                }
                start = time()
                r = requests.post(
                    url,
                    headers={
                        "api-key": openai.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response = json.loads(r.text)
                elapsed = time() - start
                if (
                    "choices" in response
                    and len(response["choices"])
                    and response["choices"][0]["finish_reason"] != "stop"
                ):
                    raise Exception("custom content moderation triggered")
                if "usage" not in response:
                    raise ValueError(response["error"]["message"])
                success = True
                return response
            except Exception as e:
                err = str(e)
                if (
                    "Azure OpenAI’s content management policy" in err
                    or "The server is currently overloaded with other requests" in err
                    or "custom content moderation triggered" in err
                ):
                    # fallback to openai method
                    payload = self.openai_completion(
                        model_name=model_name,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        stop=stop,
                    )
                    return payload
        payload["elapsed"] = elapsed
        return payload
