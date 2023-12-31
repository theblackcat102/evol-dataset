import os
from evolinstruct import EvolInstruction

if __name__ == "__main__":
    evol = EvolInstruction(
        model_name="gpt-3.5-turbo",
        backend="openai",
        backend_settings={"api_key": os.getenv("OPENAI_KEY")},
    )
    res = evol.augment("Hi how are you?", ["addition", "breath", "complexity"])
    print(res)
    evol = EvolInstruction(
        model_name="claude-1.3",
        backend="anthropic",
        backend_settings={"api_key": os.getenv("ANTHROPIC_API_KEY")},
    )
    res = evol.augment("Hi how are you?", ["addition", "breath", "complexity"])
    print(res)
