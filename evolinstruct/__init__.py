import os
import json
import uuid
import random
from tqdm import tqdm
from typing import List, Optional, Union
from .instructions import create_prompt, reject_response
from .autocompletes.openai import OpenAICompletion


class EvolInstruction:
    """
    base class for systematically augment dataset
    """

    def __init__(self, model_name, backend="openai", backend_settings={}) -> None:
        self.model_name = model_name
        if backend == "openai":
            self.backend = OpenAICompletion(**backend_settings)
        elif backend == "test":
            self.backend = None
        else:
            raise ValueError(
                f"backend {backend} is currently not supported, supported backends openai, anthropic"
            )

    def sample_task(self, available_tasks: list):
        if isinstance(available_tasks[0], str):
            task_choice = available_tasks
            task_weights = [1 / len(task_choice) for _ in range(len(available_tasks))]
        elif isinstance(available_tasks[0], tuple):
            task_choice = [t[0] for t in available_tasks]
            task_weights = [t[1] for t in available_tasks]
        c = random.choices(task_choice, task_weights, k=1)[0]
        return c

    def augment(self, text: Union[str, list], available_tasks: list):
        task = self.sample_task(available_tasks)
        input_text = create_prompt(text, task)
        text, response = self.backend.completion(input_text, model_name=self.model_name)
        return text, response, task

    def get_strategy(self, strategy):
        if strategy == "all":
            return [
                "addition",
                "breath",
                "complexity",
                "concretizing",
                "deepening",
                "diversion",
                "increase",
                "misdirection",
                "reasoning",
            ]
        elif strategy == "partial":
            return [
                "breath",
                "reasoning",
                "concretizing",
                "deepening",
            ]
        else:
            raise ValueError("doesnt support")

    def cache_result(self, new_prompt, res, task, input, curr_round):
        with open(self.cache_file, "a") as fout:
            fout.write(
                json.dumps(
                    {
                        "uuid": str(uuid.uuid4().hex),
                        "input": input,
                        "new_prompt": new_prompt,
                        "round": curr_round,
                        "response": res,
                        "task": task,
                    }
                )
                + "\n"
            )

    def ingest(
        self, texts, project_name, num_rounds=5, strategy="all", total_augment=-1
    ):
        cache_file = project_name + ".jsonl"
        added = set()
        if total_augment <= 0:
            total_augment = int(len(texts) * 2)
        curr_round = 0
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                for line in f:
                    payload = json.loads(line)
                    curr_round = max(curr_round, payload["round"])
                    added.add(payload["input"])
                    added.add(payload["new_prompt"])
                    total_augment -= 1
        self.cache_file = cache_file
        available_task = self.get_strategy(strategy)

        if curr_round <= 0:
            for text in tqdm(texts, dynamic_ncols=True):
                if text not in added:
                    new_prompt, res, task = self.augment(text, available_task)
                    if reject_response(new_prompt):
                        # we will try it in the next round
                        added.add(text)
                        continue
                    self.cache_result(new_prompt, res, task, text, curr_round)
                    added.add(new_prompt)
                total_augment -= 1
            curr_round += 1

        if total_augment > 0:
            with tqdm(total=total_augment, dynamic_ncols=True) as pbar:
                while len(added):
                    input_text = next(iter(added))
                    new_prompt, res, task = self.augment(input_text, available_task)
                    if reject_response(new_prompt):
                        continue
                    self.cache_result(new_prompt, res, task, input_text, curr_round)
                    added.remove(input_text)
                    added.add(new_prompt)
                    pbar.update(1)
                    total_augment -= 1
                    if total_augment == 0:
                        break
        print("augmentation finished!")
        augmented = []
        with open(self.cache_file, "r") as f:
            for line in f:
                payload = json.loads(line)
                augmented.append(payload["new_prompt"])
        return augmented
