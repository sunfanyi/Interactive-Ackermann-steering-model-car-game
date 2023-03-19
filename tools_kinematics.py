# -*- coding: utf-8 -*-
# @File    : tools_kinematics.py
# @Time    : 16/02/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm


import numpy as np
import sympy as sp
from IPython.display import display, Math


def get_mat_rolling(alpha, beta, L):
    res = sp.Matrix([sp.sin(alpha+beta), -sp.cos(alpha+beta), -L*sp.cos(beta)]).T
    res.simplify()
    return res


def get_mat_no_sliding(alpha, beta, L):
    res = sp.Matrix([sp.cos(alpha+beta), sp.sin(alpha+beta), L*sp.sin(beta)]).T
    res.simplify()
    return res


def rotation(theta, direction):
    if direction == 'x':
        R = sp.Matrix([[1, 0, 0],
                       [0, sp.cos(theta), -sp.sin(theta)],
                       [0, sp.sin(theta), sp.cos(theta)]])
    elif direction == 'y':
        R = sp.Matrix([[sp.cos(theta), 0, sp.sin(theta)],
                       [0, 1, 0],
                       [-sp.sin(theta), 0, sp.cos(theta)]])
    elif direction == 'z':
        R = sp.Matrix([[sp.cos(theta), -sp.sin(theta), 0],
                       [sp.sin(theta), sp.cos(theta), 0],
                       [0, 0, 1]])
    return R


def add_translation(R, t=sp.Matrix([0, 0, 0, 1])):
    T = R.row_insert(len(R), sp.Matrix([[0, 0, 0]]))
    T = T.col_insert(len(T), t)
    return T


def eqnprint(symbol, alias=None, expression=None, ans=None):
    if ans is None:
        display(Math(f'{symbol.subs(alias)}={expression.subs(alias)}'))
    elif expression is None:
        display(Math(f'{symbol.subs(alias)}={ans}'))
    else:
        display(Math(f'{symbol.subs(alias)}={expression.subs(alias)}={ans}'))


def symprint(symbol, sup, sub, dot=False):
    if dot == 1:
        symbol = r'\dot{%s}' % symbol
    elif dot == 2:
        symbol = r'\ddot{%s}' % symbol
    if sup == '':
        info = r"{}_{}".format(symbol, sub)
    else:
        info = r"^{}{}_{}".format(sup, symbol, sub)
    display(sp.symbols(info))


def matprint(matrix, alias=None):
    if alias:
        display(matrix.subs(alias))
    else:
        display(matrix)


