import inspect


class A:
    def __init__(self):
        caller_file = inspect.stack()[1].filename
        print(caller_file)