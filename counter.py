import time

class Counter:

    def __init__(self, formatMessage):
        self.formatMessage = formatMessage
        self.counter = 0
        self.lastPrinted = 0
        self.oldMinute = time.time()
        self.history = list()

    def increment(self, amount = 1):
        self.counter += amount

        if self.__minute_elapsed():
            self.history.append(self.counter - self.lastPrinted)
            print(self.formatMessage.format(str(self.counter - self.lastPrinted), self.__average()))
            self.__printed()

    def __minute_elapsed(self):
        return time.time() - self.oldMinute >= 60

    def __printed(self):
        self.lastPrinted = self.counter
        self.oldMinute = time.time()

    def __average(self):
        length = len(self.history)
        if length == 0:
            # we dont want to divide by zero
            length += 1
        return sum(self.history) / length