import random
from typing import List, Optional, Union
from autocompletes.openai import OpenAICompletion


class EvolInstruction:
    """
    base class for systematically augment dataset
    """

    def __init__(self, backend="openai", backend_settings={}) -> None:
        if backend == "openai":
            self.backend = OpenAICompletion(**backend_settings)
        else:
            raise ValueError(
                f"backend {backend} is currently not supported, supported backends openai, anthropic"
            )

    def augment(self, text: Union[str, list], available_tasks: list):
        if isinstance(available_tasks[0], str):
            task_choice = available_tasks
            task_weights = [1 / len(task_choice) for _ in range(len(available_tasks))]
        elif isinstance(available_tasks[0], tuple):
            task_choice = [t[0] for t in available_tasks]
            task_weights = [t[1] for t in available_tasks]
        c = random.choice(population=task_choice, weights=task_weights, k=1)
