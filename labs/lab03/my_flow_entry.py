import json
import os

from dotenv import load_dotenv
from pathlib import Path
from typing import TypedDict, List
import numpy as np

from promptflow.core import log_metric, tool
from promptflow.tracing import trace
from promptflow.core import Prompty, AzureOpenAIModelConfiguration

BASE_DIR = Path(__file__).absolute().parent


class WeatherInfo(TypedDict):
    location: str
    temperature: float
    format: str
    forecast: list[str]
    num_days: int


def get_current_weather(location, format="fahrenheit"):
    """Get the current weather in a given location"""
    return WeatherInfo(
        location=location, temperature="72", format=format, forecast=["sunny", "windy"]
    )


def get_n_day_weather_forecast(location, format, num_days):
    """Get next num_days weather in a given location"""
    return WeatherInfo(
        location=location,
        temperature="60",
        format=format,
        forecast=["rainy"],
        num_days=num_days,
    )

def test_me(text: str) -> str:
    return f"Test function: {text}"

@trace
def run_function(response_message: dict) -> str:
    if "tool_calls" in response_message and len(response_message["tool_calls"]) == 1:
        call = response_message["tool_calls"][0]
        function = call["function"]
        function_name = function["name"]
        function_args = json.loads(function["arguments"])
        print(function_args)
        result = globals()[function_name](**function_args)

        return str(result)

    print("No function call")

    if isinstance(response_message, dict):
        result = response_message["content"]
    else:
        result = response_message
    return result


def reduce_history(
    prompty: Prompty = None,
    chat_history: list = None,
    max_total_token=2048,
    **kwargs,
) -> object:
    """Reduce the chat_history given the prompt and any additional inputs."""

    chat_history = chat_history or []

    while len(chat_history) > 0:
        token_count = prompty.estimate_token_count(
            chat_history=chat_history, **kwargs
        )
        if token_count > MAX_TOTAL_TOKEN:
            chat_history = chat_history[1:]
            print(
                f"Reducing chat history count to {len(chat_history)} to fit token limit"
            )
        else:
            break
    return chat_history


MAX_TOTAL_TOKEN = 2048


@trace
def chat(
    question: str = "What's the weather of Beijing?",
    chat_history: list = None,
    max_total_token=2048,
) -> str:
    """Flow entry function."""

    if "OPENAI_API_KEY" not in os.environ and "AZURE_OPENAI_API_KEY" not in os.environ:
        # load environment variables from .env file
        load_dotenv()

    prompty = Prompty.load(source=BASE_DIR / "chat_with_tools.prompty")

    chat_history = chat_history or []
    # Try to render the prompt with token limit and reduce the history count if it fails
    reduced_history = reduce_history(prompty, chat_history, max_total_token)

    output = prompty(question=question, chat_history=reduced_history)

    function_output = run_function(output)

    return function_output


def restate_question(
    question: str = "What is the capital of Japan?",
    chat_history: list = None
) -> str:
    """Restate the question based on the chat history."""

    model_config = AzureOpenAIModelConfiguration

    if "OPENAI_API_KEY" not in os.environ and "AZURE_OPENAI_API_KEY" not in os.environ:
        # load environment variables from .env file
        load_dotenv()

    restate_question_prompty = Prompty.load(source=BASE_DIR / "restate_question.prompty")
    restated_question = restate_question_prompty(question=question, chat_history=chat_history)
    return restated_question

class EvalFlow:
    def __init__(self, model_config: AzureOpenAIModelConfiguration):
        self.model_config = model_config

    def __call__(self, chat_history: list, question: str, answer: str, ground_truth: str, model_config: AzureOpenAIModelConfiguration):
        self.model_config = model_config
        """Check the correctness of the answer """
        examples = [ 
            {
                "chat_history": None,
                "question": 'What is the capital of Japan?',
                "answer": "Paris",
                "ground_truth": "Tokyo"
            }
        ]
        prompty = Prompty.load(
            source=BASE_DIR / "eval.prompty",
            model={"configuration": model_config},
        )
        results = prompty(examples=examples, chat_history=chat_history, question=question, answer=answer, ground_truth=ground_truth)
        #results = json.loads(results)
        return results

    def __aggregate__(self, line_results: list) -> dict:
        """Aggregate the results."""
        total = len(line_results)
        metric_key = "average_correctness"
        metric_value = (
            sum(int(r["score"]) for r in line_results) / total
        )
        log_metric("average_correctness", metric_value) # TODO: Not working locally; need to resolve
        return {
            "average_correctness": metric_value,
        }

if __name__ == "__main__":
    from promptflow.tracing import start_trace

    start_trace()

    config = AzureOpenAIModelConfiguration(
        connection="open_ai_connection", azure_deployment="gpt-4-1106"
    )
    evaluator = EvalFlow(model_config=config)
    eval_result=evaluator.__call__(chat_history=None, question='What is the weather of Beijing', answer='Paris', ground_truth='Tokyo', model_config=config)  
    print(f'***EVAL***\n{eval_result}')
    chat_result = chat("What's the weather of Beijing?")
    print(f'***CHAT RESULT***\n{chat_result}')
