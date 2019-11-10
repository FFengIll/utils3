
# this is a python standard library
from contextlib import contextmanager


class Indent:
    def __init__(self, word='\t', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 0
        self.word = word

    @contextmanager
    def __call__(self):
        self.level += 1
        yield
        self.level -= 1

    @contextmanager
    def indent(self):
        self.level += 1
        yield
        self.level -= 1

    def __str__(self):
        return self.word * self.level


if __name__ == "__main__":
    indent = Indent('****')

    with indent():
        print(indent, 1)
        with indent():
            print(indent, 1)
