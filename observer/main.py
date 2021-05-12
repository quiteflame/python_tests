class Sink(object):
    def __init__(self, value):
        self.container = []
        self.value = value

    def append(self, element):
        self.container.append(element)

    def drain(self):
        previous = self.value
        for element in self.container:
            if callable(element):
                previous = element(previous)
                if type(previous) is Observable:
                    previous = previous.sink.drain()
            else:
                raise Exception(f"Not supported type: {element}")

        return previous


class Observable(object):
    def __init__(self, value):
        self.value = value
        self.listener = None
        self.sink = Sink(value)

    def subscribe(self, listener):
        value = self.sink.drain()
        listener(value)

    def map(self, operator):
        self.sink.append(operator)
        return self

    def flat_map(self, observable):
        self.sink.append(observable)
        return self


def name(value):
    name = Observable(value) \
        .map(lambda x: x + "K") \
        .map(lambda x: x + "a") \
        .map(lambda x: x + "r") \
        .map(lambda x: x + "o") \
        .map(lambda x: x + "l")

    return name


def lastname(value):
    lastname = Observable(value) \
        .map(lambda x: x + "M") \
        .map(lambda x: x + "o") \
        .map(lambda x: x + "l") \
        .map(lambda x: x + "u") \
        .map(lambda x: x + "s") \
        .map(lambda x: x + "z") \
        .map(lambda x: x + "y") \
        .map(lambda x: x + "s")

    return lastname


if __name__ == '__main__':
    Observable("Hi")\
        .flat_map(lambda x: name(x)) \
        .flat_map(lambda x: lastname(x)) \
        .subscribe(lambda x: print(x))

