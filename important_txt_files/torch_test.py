import time
import torch
from googletrans import Translator
from functools import wraps
import logging
logging.basicConfig(level=logging.ERROR)


def timeit(func):

    @wraps(func)
    def timeit_wrapper(*args, **kwargs):

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        print(f'Function {func.__name__}, took {total_time:.4f} seconds.')

        return result

    return timeit_wrapper

@timeit
def pythorch_model():
    batch = ["long dusty road", "leftalone corpse", "green cherry", "rotten flesh"] * 8

    model = torch.hub.load(
                    "pytorch/fairseq",
                    "transformer.wmt19.en-ru.single_model",
                    tokenizer="moses",
                    bpe="fastbpe",
                    verbose=False,
                )
    model.cuda()
    print(type(model))
    for i in range(100):
        print(i)
        translation = model.translate(batch, verbose=False)
        

def main():
    pythorch_model()

main()