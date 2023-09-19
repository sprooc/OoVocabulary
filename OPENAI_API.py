import tiktoken
import openai
import os
import json
import time
class user_message:
    def __init__(self, message, model = "gpt-3.5-turbo"):
        self.message = message
        self.model = model
        self.token = 0
    
    def num_tokens(self):
        """Return the number of tokens used by a list of messages."""
        if self.token != 0:
            return self.token
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if self.model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif self.model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in self.model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return num_tokens(self.message, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in self.model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return num_tokens(self.message, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {self.model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in self.messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

class chat:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
    
    def send_message(self, message):
        openai.organization = "org-y9ZOWMdy5y4c9ztNlsKAa5sA"
        openai.api_key = os.getenv('OPENAI_API_KEY')
        completion = openai.ChatCompletion.create(model=self.model, messages=message, temperature=1, max_tokens=1000)
        response_content = completion["choices"][0]["message"]["content"]
        self.log(message, completion)
        return response_content

    def log(self, message, completion):
        f = open(file="data\log_history", mode='a+')
        f.seek(0)
        lines = f.readlines()
        history = json.loads(lines[len(lines) - 1])
        fee = GPT.calculate_price(completion)
        log = {"time": time.asctime(),
               "prompt": message,
               "completion": completion["choices"][0]["message"]["content"],
               "model": completion["model"],
               "prompt_tokens": completion["usage"]["prompt_tokens"],
               "completion_tokens": completion["usage"]["completion_tokens"],
               "total_tokens": completion["usage"]["total_tokens"],
               "fee": fee,
               "total_fee": history["total_fee"] + fee 
               }
        
        f.seek(0)
        f.writelines(json.dumps(log) +"\n")

class GPT:
    def calculate_price(completion):
        rate = 7.29 
        with open(file="data\log_price") as f:
            prices = json.loads(f.readline())
        return (prices[completion["model"]]["input"] * completion["usage"]["prompt_tokens"] / 1000 + prices[completion["model"]]["output"] * completion["usage"]["completion_tokens"] / 1000) * rate

    def update_price():
        prices = {"gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002},
                  "gpt-4-0613": {"input": 0.03, "output": 0.06}}
        with open(file="data\log_price",mode="w") as f:
            f.write(json.dumps(prices))
               