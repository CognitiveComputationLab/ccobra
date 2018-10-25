""" Syllogistic convenience class.

"""

from .parsing import encode_response, encode_task, decode_response

class Syllogism():
    def __init__(self, item):
        # Store the task
        self.item = item
        self.task = self.item.task

        # Extract useful information
        self.encoded_task = encode_task(self.task)
        self.p1 = self.task[0]
        self.p2 = self.task[1]
        self.quantifier_p1 = self.task[0][0]
        self.quantifier_p2 = self.task[1][0]

        # Figure out the figure and identify the terms
        self.figure = int(self.encoded_task[-1])
        if self.figure == 1:
            self.A, self.B, self.C = self.task[0][1], self.task[0][2], self.task[1][2]
        elif self.figure == 2:
            self.A, self.B, self.C = self.task[0][2], self.task[0][1], self.task[1][1]
        elif self.figure == 3:
            self.A, self.B, self.C = self.task[0][1], self.task[0][2], self.task[1][1]
        elif self.figure == 4:
            self.A, self.B, self.C = self.task[0][2], self.task[0][1], self.task[1][2]

    def encode_response(self, response):
        return encode_response(response, self.item.task)

    def decode_response(self, encoded_response):
        return decode_response(encoded_response, self.item.task)

    def __str__(self):
        s = 'Syllogism:\n'
        s += '\ttask: {}\n'.format(self.task)
        s += '\tencoded_task: {}\n'.format(self.encoded_task)
        s += '\tp1: {}\n'.format(self.p1)
        s += '\tp2: {}\n'.format(self.p2)
        s += '\tquantifier_p1: {}\n'.format(self.quantifier_p1)
        s += '\tquantifier_p2: {}\n'.format(self.quantifier_p2)
        s += '\tfigure: {}\n'.format(self.figure)
        s += '\tTerms:\n'
        s += '\t\tA: {}\n'.format(self.A)
        s += '\t\tB: {}\n'.format(self.B)
        s += '\t\tC: {}\n'.format(self.C)
        return s
