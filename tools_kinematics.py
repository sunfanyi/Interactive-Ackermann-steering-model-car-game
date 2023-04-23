# -*- coding: utf-8 -*-
# @File    : tools_kinematics.py
# @Time    : 16/02/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm


import numpy as np
import sympy as sp
from IPython.display import display, Math


# =============================== For visualisation in jupyter notebook ===============================
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
    else:
        raise ValueError('Direction must be x, y or z')
    return R


def add_translation(R, t=sp.Matrix([0, 0, 0, 1])):
    T = R.row_insert(len(R), sp.Matrix([[0, 0, 0]]))
    T = T.col_insert(len(T), t)
    return T


def eqnprint(symbol, alias=None, expression=None, ans=None):
    if ans is None:
        expr_latex = sp.latex(symbol.subs(alias)) + '=' + sp.latex(expression.subs(alias))
        display(Math(expr_latex))
    elif expression is None:
        display(Math(sp.latex(symbol.subs(alias)) + '=' + str(ans)))
    else:
        expr_latex = sp.latex(symbol.subs(alias)) + '=' + sp.latex(expression.subs(alias)) + '=' + str(ans)
        display(Math(expr_latex))


def get_sym(symbol, sub='', sup='', dot=False, show=False):
    if (sup == '') & (sub == ''):
        info = r"{}".format(symbol)
    elif sup == '':
        info = r"{}_{{{}}}".format(symbol, sub)
    elif sub == '':
        info = r"^{}{}".format(sup, symbol)
    else:
        info = r"^{{{}}}{}_{{{}}}".format(sup, symbol, sub)

    if dot == 1:
        info = r'\dot{%s}' % info
    elif dot == 2:
        info = r'\ddot{%s}' % info

    if show:
        display(sp.symbols(info))

    return sp.symbols(info)


def matprint(matrix, alias=None):
    if alias:
        display(matrix.subs(alias))
    else:
        display(matrix)


# =============================== For trajectory planning ===============================
def get_trans_mat(a, alpha, d, theta, return_P=False):
    """
    Obtain the transformation matrix from DH Parameters
    :param a: Link length
    :param alpha: Link twist (in deg)
    :param d: Link offset
    :param theta: Joint angle (in deg)
    :param return_P: return the 3x1 translation matrix
    :return: transformation matrix and rotation matrix
    """
    if type(alpha) == int or type(alpha) == float:
        alpha = alpha*np.pi/180
    if type(theta) == int or type(theta) == float:
        theta = theta*np.pi/180

    R = rotation(alpha, 'x') * rotation(theta, 'z')
    R.simplify()
    T = add_translation(R, sp.Matrix([a, -sp.sin(alpha) * d, sp.cos(alpha) * d, 1]))
    if return_P:
        return R, T, sp.Matrix([a, -sp.sin(alpha) * d, sp.cos(alpha) * d])
    else:
        return R, T


def update_target_vals(T0e_target, initial_vals):
    """
    get the target values from the position of end effector which can be used
    for inverse kinematics
    :param T0e_target: matrix of the position of end effector
    :param initial_vals: a dict containing all the keys, eg.
        initial_vals = {r11: None, r12: None, r13: None,
                        r21: None, r22: None, r23: None,
                        r31: None, r32: None, r33: None,
                        X: None, Y: None, Z: None}
        where the rii, X, Y, Z are sympy symbols
    :return: a dict containing target rii, X, Y, Z values, which can be
        substituted easily to equation by .subs(vals), eg.
    """
    keys = list(initial_vals.keys())  # take the keys
    # update the values
    vals = {keys[0]: T0e_target[0, 0], keys[1]: T0e_target[0, 1], keys[2]: T0e_target[0, 2],
            keys[3]: T0e_target[1, 0], keys[4]: T0e_target[1, 1], keys[5]: T0e_target[1, 2],
            keys[6]: T0e_target[2, 0], keys[7]: T0e_target[2, 1], keys[8]: T0e_target[2, 2],
            keys[9]: T0e_target[0, 3], keys[10]: T0e_target[1, 3], keys[11]: T0e_target[2, 3]}
    return vals


def calc_parabolic_traj_via_points(t, theta_pre, theta_dot_pre, V, a_left,
                                   a_right, tb_left, tb_right):
    """
    Linear and Parabolic Blended Trajectories with via points
    """
    tf = t[-1]
    theta_vals = np.ndarray(np.shape(t))  # position
    theta_velo = np.ndarray(np.shape(t))  # velocity
    theta_acc = np.ndarray(np.shape(t))  # acceleration

    range1 = (t >= 0) & (t <= tb_left)
    a0 = theta_pre
    a1 = theta_dot_pre
    a2 = a_left/2
    theta_vals[range1] = a0 + a1*t[range1] + a2*t[range1]**2
    theta_velo[range1] = a1 + 2*a2*t[range1]
    theta_acc[range1] = 2*a2

    range2 = (t > tb_left) & (t <= tf-tb_right)
    a0 = theta_pre + tb_left*(theta_dot_pre-V) + a_left/2*tb_left**2
    a1 = V
    a2 = 0
    theta_vals[range2] = a0 + a1*t[range2] + a2*t[range2]**2
    theta_velo[range2] = a1 + 2*a2*t[range2]
    theta_acc[range2] = 2*a2
    theta_ideal = a0 + a1*t + a2*t**2

    range3 = (t > tf-tb_right) & (t <= tf)
    a1 = V - a_right * (tf - tb_right)
    a2 = a_right/2
    a0 = theta_pre + tb_left*(theta_dot_pre-V) + a_left/2*tb_left**2 + \
                        (tf - tb_right) * (V - a1) - (tf - tb_right)**2 * a2
    theta_vals[range3] = a0 + a1*t[range3] + a2*t[range3]**2
    theta_velo[range3] = a1 + 2*a2*t[range3]
    theta_acc[range3] = 2*a2

    return theta_vals, theta_velo, theta_acc, theta_ideal
