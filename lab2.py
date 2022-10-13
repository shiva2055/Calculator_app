# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 21:02:26 2022

@author: shiva
"""
import math

import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import re
from collections import namedtuple
from collections import deque
from tokenize import tokenize
from io import BytesIO
from pprint import pprint as pp

Window.size = (800, 800)
# .kv design file
Builder.load_file('calculator.kv')


class MyLayout(Widget):
    def clear(self):
        self.ids.calc_input.text = ''

    # creating button functions
    def button_press(self, button):
        # create variable to store number in text button
        prior = self.ids.calc_input.text
        if "Error" in prior:
            prior = ""
        if prior == "0":
            self.ids.calc_input.text = ''
            self.ids.calc_input.text = f'{button}'
        else:
            self.ids.calc_input.text = f'{prior}{button}'

    # makes pos or neg
    def pos_neg(self):
        prior = self.ids.calc_input.text
        # test prior neg sign
        if "-" in prior:
            self.ids.calc_input.text = f'{prior.replace("-", "")}'
        else:
            self.ids.calc_input.text = f'-{prior}'

    # clearing the input
    def remove(self):
        prior = self.ids.calc_input.text
        prior = prior[:-1]
        self.ids.calc_input.text = prior

    # checking if its digit or a dot
    def is_digits(self, digit):
        if digit == '0' or digit == '1' or digit == '2' or digit == '3' or digit == '4' or digit == '5' \
                or digit == '6' or digit == '7' or digit == '8' or digit == '9' or digit == '.':
            return True
        else:
            return False

    # checking if its float
    def isfloat(self, digit):
        try:
            float(digit)
            return True
        except ValueError:
            return False

    # using shaunting-yard algorithm
    OpInfo = namedtuple('OpInfo', 'prec assoc')
    L, R = 'Left Right'.split()

    ops = {
        '^': OpInfo(prec=4, assoc=R),
        '*': OpInfo(prec=3, assoc=L),
        '/': OpInfo(prec=3, assoc=L),
        '+': OpInfo(prec=2, assoc=L),
        '-': OpInfo(prec=2, assoc=L),
        '(': OpInfo(prec=5, assoc=L),
        ')': OpInfo(prec=0, assoc=L),
        'sin': OpInfo(prec=4, assoc=R),
        'cos': OpInfo(prec=4, assoc=R),
        'tan': OpInfo(prec=4, assoc=R),
        'cot': OpInfo(prec=4, assoc=R),
        'ln': OpInfo(prec=4, assoc=R),
        'log': OpInfo(prec=4, assoc=R),
        '{': OpInfo(prec=6, assoc=L),
        '}': OpInfo(prec=0, assoc=L),

    }

    NUM, LPAREN, RPAREN = 'NUMBER ( )'.split()

    def get_input(self, inp=None):
        'Inputs an expression and returns list of (TOKENTYPE, tokenvalue)'

        if inp is None:
            inp = input('expression: ')
        tokens = inp.strip().split()
        tokenvals = []
        for token in tokens:
            if token in self.ops:
                tokenvals.append((token, self.ops[token]))
            # elif token in (LPAREN, RPAREN):
            #    tokenvals.append((token, token))
            else:
                tokenvals.append((self.NUM, token))
        return tokenvals

    def shunting(self, tokenvals):
        outq, stack = [], []
        table = ['TOKEN,ACTION,RPN OUTPUT,OP STACK,NOTES'.split(',')]
        for token, val in tokenvals:
            note = action = ''
            if token is self.NUM:
                action = 'Add number to output'
                outq.append(val)
                table.append((val, action, ' '.join(outq), ' '.join(s[0] for s in stack), note))
            elif token in self.ops:
                t1, (p1, a1) = token, val
                v = t1
                note = 'Pop ops from stack to output'
                while stack:
                    t2, (p2, a2) = stack[-1]
                    if (a1 == self.L and p1 <= p2) or (a1 == self.R and p1 < p2):
                        if t1 != self.RPAREN:
                            if t2 != self.LPAREN:
                                stack.pop()
                                action = '(Pop op)'
                                outq.append(t2)
                            else:
                                break
                        else:
                            if t2 != self.LPAREN:
                                stack.pop()
                                action = '(Pop op)'
                                outq.append(t2)
                            else:
                                stack.pop()
                                action = '(Pop & discard "(")'
                                table.append((v, action, ' '.join(outq), ' '.join(s[0] for s in stack), note))
                                break
                        table.append((v, action, ' '.join(outq), ' '.join(s[0] for s in stack), note))
                        v = note = ''
                    else:
                        note = ''
                        break
                    note = ''
                note = ''
                if t1 != self.RPAREN:
                    stack.append((token, val))
                    action = 'Push op token to stack'
                else:
                    action = 'Discard ")"'
                table.append((v, action, ' '.join(outq), ' '.join(s[0] for s in stack), note))
        note = 'Drain stack to output'
        while stack:
            v = ''
            t2, (p2, a2) = stack[-1]
            action = '(Pop op)'
            stack.pop()
            outq.append(t2)
            table.append((v, action, ' '.join(outq), ' '.join(s[0] for s in stack), note))
            v = note = ''
        return table

    def dot(self):
        prior = self.ids.calc_input.text

        stack = []
        for i in reversed(prior):
            if i.isdigit():
                stack.append(i)
            elif i == ".":
                stack.append(i)
            else:
                break

        if "." in stack:
            pass
        else:
            prior = f'{prior}.'
            # outputs back to text box
            self.ids.calc_input.text = prior

    # button click for trig functions
    def function(self, sign):
        prior = self.ids.calc_input.text
        if "Error" in prior:
            prior = ""
        self.ids.calc_input.text = f'{prior}{sign}'

    # button click for operands
    def math_sign(self, sign):
        prior = self.ids.calc_input.text
        # if error in textinput, it removes the text
        if "Error" in prior:
            prior = ""
        # if text input is empty it puts math sign
        elif prior == "":
            self.ids.calc_input.text = f'{prior}{sign}'

        # double  - unary operator gives +
        # elif prior != "" and sign == "-" and prior[-1] == "-":
        # self.ids.calc_input.text = f'{""}'

        # checks if unary operator in last element, adds space for proper parsing
        elif sign == "( " and prior[-1] == "-":
            self.ids.calc_input.text = f'{prior}{" "}{sign}'

        # checks if user inputs opening bracket and last element is either number or closing bracket, it '*' in between
        elif (sign == "( " and prior[-1] == ")") or (sign == "( " and prior[-1].isdigit()):
            self.ids.calc_input.text = f'{prior}{" * "}{sign}'

        # checks if its ( or { or - it adds to textinput or screen
        elif sign == "( " or sign == "{ " or sign == '-':
            self.ids.calc_input.text = f'{prior}{sign}'

        # if our expression is empty, it doesn't allow operator at first before number
        elif len(prior) == 0:
            pass

        # checks for condition if operator is last element in expression, and user adds another operator.
        # It doesn't allow two operators together
        else:
            if len(prior) > 1:
                if "+" in prior[-2]:
                    pass
                elif "*" in prior[-2]:
                    pass
                elif "/" in prior[-2]:
                    pass
                else:
                    self.ids.calc_input.text = f'{prior}{sign}'

            elif len(prior) == 1:
                if "+" in prior[-1]:
                    pass
                elif "*" in prior[-1]:
                    pass
                elif "/" in prior[-1]:
                    pass
                else:
                    self.ids.calc_input.text = f'{prior}{sign}'

    # The main function that converts given infix expression
    # to postfix expression
    def evalRPN(self, tokens) -> float:
        list = ['sin', 'cos', 'cot', 'tan', 'ln', 'log']
        stack = []
        for t in tokens:

            # if it is digit, it adds to stack
            if t not in {"+", "-", "*", "/", "^"} and t not in list:

                # checking unary '-', if multiple '-', check if even or odd number of minus
                # change the number accordingly
                count = 0
                number = []
                if "-" in t:

                    for i in t:
                        if i == "-":
                            count += 1
                        else:
                            number.append(i)

                    number = ''.join(number)
                    t = number
                    if count % 2 == 1:
                        number = -1 * float(number)
                        t = number


                # checks if element is not digit, operator or trig func, it throws error
                try:
                    stack.append(float(t) if '.' in str(t) else float(t))
                except:
                    return ("Error")

            # adds tric func to stack
            else:
                if t in list:
                    b = stack.pop()
                    if t == "sin":
                        # changes radians to degrees
                        stack.append(math.sin(math.radians(b)))
                    elif t == "cos":
                        stack.append(math.cos(math.radians(b)))
                    elif t == "tan":
                        stack.append(math.tan(math.radians(b)))
                    elif t == "ln":
                        stack.append(math.log(b))
                    elif t == "log":
                        stack.append(math.log10(b))
                    else:
                        stack.append(1 / (math.tan(math.radians(b))))
                else:
                    # checks if -2 equals to 0-2 or +2 to 0+2 or /2 to 0/2 and *2 to 0*2
                    # adds 0 if only one operand
                    if (t == '-' and len(stack) == 1) or (t == '+' and len(stack) == 1) \
                            or (t == '/' and len(stack) == 1) or (t == '*' and len(stack) == 1):
                        stack.insert(0, 0)
                    #print(stack)
                    b, a = stack.pop(), stack.pop()
                    if t == "+":
                        stack.append(a + b)
                    elif t == "-":
                        stack.append(a - b)
                    elif t == "*":
                        stack.append(a * b)
                    elif t == "^":
                        stack.append(pow(a, b))
                    else:
                        stack.append(a / b)
        return stack[0]

    def equal(self):
        try:
            prior = self.ids.calc_input.text

            # checking empty textinput
            if prior == "":
                return

            # checking for expression ending with number and not allowing expression ending with operator
            elif (len(prior) is not 0) and not (prior[-1].isdigit()) and (prior[-1] != ")"):
                self.ids.calc_input.text = f'{"Error"}'
                return 0

            # else calculating expression
            else:

                tokenvals = self.get_input(prior)
                # print("tokenvals", tokenvals)
                postfix = self.shunting(tokenvals)[-1][2].split()
                # print("postfix", postfix)

                answer = self.evalRPN(postfix)
                # print("answer: ", answer)
                # print in textbox
                self.ids.calc_input.text = f'{str(answer)}'
        except:
            # checks value error
            if ValueError:
                self.ids.calc_input.text = f'{"Value Error"}'
            # checks overflow error
            elif OverflowError:
                self.ids.calc_input.text = f'{"OverFlow Error"}'


# Calculator app class

class CalculatorApp(App):
    def build(self):
        return MyLayout()


# main
if __name__ == '__main__':
    CalculatorApp().run()
