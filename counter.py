import time

class Counter:

    def __init__(self, formatMessage):
        self.formatMessage = formatMessage
        self.counter = 0
        self.lastPrinted = 0
        self.oldMinute = time.time()

    def increment(self):
        self.counter += 1

        if self.__minute_elapsed():
            print(format(self.formatMessage), self.counter - self.lastPrinted)
            self.__printed()

    def __minute_elapsed(self):
        return time.time() - self.oldMinute >= 60

    def __printed(self):
        self.lastPrinted = self.counter
        self.oldMinute = time.time()