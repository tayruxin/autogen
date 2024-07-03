from types import SimpleNamespace
import os

from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

import autogen
from autogen import AssistantAgent, UserProxyAgent


# custom client with custom model loader
class CustomModelClient:
    def __init__(self, config, **kwargs):
        print(f"CustomModelClient config: {config}")
        self.device = config.get("device", "cpu")
        self.model = AutoModelForCausalLM.from_pretrained(config["model"]).to(self.device)
        self.model_name = config["model"]
        self.tokenizer = AutoTokenizer.from_pretrained(config["model"], use_fast=False)
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        # params are set by the user and consumed by the user since they are providing a custom model
        # so anything can be done here
        gen_config_params = config.get("params", {})
        self.max_length = gen_config_params.get("max_length", 256)

        print(f"Loaded model {config['model']} to {self.device}")

    def create(self, params):
        if params.get("stream", False) and "messages" in params:
            raise NotImplementedError("Local models do not support streaming.")
        else:
            num_of_responses = params.get("n", 1)

            # can create my own data response class
            # here using SimpleNamespace for simplicity
            # as long as it adheres to the ClientResponseProtocol

            response = SimpleNamespace()

            inputs = self.tokenizer.apply_chat_template(
                params["messages"], return_tensors="pt", add_generation_prompt=True
            ).to(self.device)
            inputs_length = inputs.shape[-1]

            # add inputs_length to max_length
            max_length = self.max_length + inputs_length
            generation_config = GenerationConfig(
                max_length=max_length,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            response.choices = []
            response.model = self.model_name

            for _ in range(num_of_responses):
                outputs = self.model.generate(inputs, generation_config=generation_config)
                # Decode only the newly generated text, excluding the prompt
                text = self.tokenizer.decode(outputs[0, inputs_length:])
                choice = SimpleNamespace()
                choice.message = SimpleNamespace()
                choice.message.content = text
                choice.message.function_call = None
                response.choices.append(choice)

            return response

    def message_retrieval(self, response):
        """Retrieve the messages from the response."""
        choices = response.choices
        return [choice.message.content for choice in choices]

    def cost(self, response) -> float:
        """Calculate the cost of the response."""
        response.cost = 0
        return 0

    @staticmethod
    def get_usage(response):
        # returns a dict of prompt_tokens, completion_tokens, total_tokens, cost, model
        # if usage needs to be tracked, else None
        return {}
    


config_list_custom = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={"model_client_cls": ["CustomModelClient"]},
)


assistant = AssistantAgent("assistant", llm_config={"config_list": config_list_custom})
user_proxy = UserProxyAgent(
    "user_proxy",
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    },
)
    

assistant.register_model_client(model_client_cls=CustomModelClient)


user_proxy.initiate_chat(assistant, message="Write python code to print Hello World!")