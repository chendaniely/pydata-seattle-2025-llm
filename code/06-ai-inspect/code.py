# from: https://posit-dev.github.io/chatlas/misc/evals.html
#
# pip install 'chatlas[eval]'
# pip install -U git+https://github.com/posit-dev/chatlas
#
# run in terminal:
#
# inspect eval code.py
#
# inspect view
#

from chatlas import ChatOpenAI
from inspect_ai import Task, task
from inspect_ai.dataset import csv_dataset
from inspect_ai.scorer import model_graded_qa

chat = ChatOpenAI()


@task
def my_eval():
    return Task(
        dataset=csv_dataset("eval.csv"),
        solver=chat.to_solver(),
        scorer=model_graded_qa(model="openai/gpt-4o-mini"),
    )
