from evolinstruct import EvolInstruction


if __name__ == "__main__":
    evol = EvolInstruction(backend="test")
    c = evol.sample_task(["addition", "breath", "complexity"])
    print(c)
    c = evol.sample_task([("addition", 0.9), ("breath", 0.05), ("complexity", 0.05)])
    print(c)
