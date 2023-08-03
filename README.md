# Evol Dataset (WIP)

A tool to augment and "evol" any instruction or chat based dataset to increase the language space.


## Simple instruction

Using alpaca as example to augment new sets of instruction

```python
from datasets import load_dataset
dataset = load_dataset("tatsu-lab/alpaca")["train"]
texts = []
for row in dataset:
    input_text = row["instruction"]
    if len(row["input"]):
        input_text += "## Input:\n" + row["input"]
    texts.append(input_text)
    if len(texts) > 10:
        break

## augment using evolution strategy

import os
from evolinstruct import EvolInstruction
evol = EvolInstruction(
    model_name="gpt-3.5-turbo",
    backend="openai",
    backend_settings={"api_key": os.getenv("OPENAI_KEY")},
)
results = evol.ingest(texts, 'alpaca_evol_sample', total_augment=20)
print(results[:10])
```



TODO:


[ ] create datasets supported library, able to augment any hf datasets

[ ] add probabilistic markov chain for state transition as in Xu, Can et al (original wizardlm only have determinstic transition )


## Disclaimer

The resources, including code, data, and model weights, associated with this project are restricted for academic research purposes only and cannot be used for commercial purposes. The content produced by any version of WizardCoder is influenced by uncontrollable variables such as randomness, and therefore, the accuracy of the output cannot be guaranteed by this project. This project does not accept any legal liability for the content of the model output, nor does it assume responsibility for any losses incurred due to the use of associated resources and output results.

## Citation

```
@article{Xu2023WizardLMEL,
  title={WizardLM: Empowering Large Language Models to Follow Complex Instructions},
  author={Can Xu and Qingfeng Sun and Kai Zheng and Xiubo Geng and Pu Zhao and Jiazhan Feng and Chongyang Tao and Daxin Jiang},
  journal={ArXiv},
  year={2023},
  volume={abs/2304.12244}
}
```

```
@misc{luo2023wizardcoder,
      title={WizardCoder: Empowering Code Large Language Models with Evol-Instruct},
      author={Ziyang Luo and Can Xu and Pu Zhao and Qingfeng Sun and Xiubo Geng and Wenxiang Hu and Chongyang Tao and Jing Ma and Qingwei Lin and Daxin Jiang},
      year={2023},
}
```
