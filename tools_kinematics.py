# -*- coding: utf-8 -*-
# @File    : tools_kinematics.py
# @Time    : 06/02/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm


import numpy as np
from sympy import *
from IPython.display import display, Math


def plot_links(ax, links, show_coor=False):
    for i in range(len(links)-1):
        P1 = links[i][:3]
        P2 = links[i+1][:3]
        ax.plot([P1[0], P2[0]], [P1[1], P2[1]], [P1[2], P2[2]], 'b-')
        ax.plot([P1[0]], [P1[1]], [P1[2]], 'bx')

        if show_coor:
            P1 = [round(i) for i in P1]
            P2 = [round(i) for i in P2]
            if P1 != P2:
                ax.text(P1[0] - 10, P1[1], P1[2] + 3, str(P1))
    if show_coor:
        ax.text(P2[0] - 10, P2[1], P2[2] - 15, str(P2))


def plot_links_moving(line1, line2, links):
    link_data = [[], [], []]
    joint_data = [[], [], []]
    for i in range(len(links)-1):
        P1 = links[i][:3]
        P2 = links[i+1][:3]

        # Link line
        link_data[0].extend([P1[0], P2[0]])
        link_data[1].extend([P1[1], P2[1]])
        link_data[2].extend([P1[2], P2[2]])

        # Joint point
        joint_data[0].extend([P1[0]])
        joint_data[1].extend([P1[1]])
        joint_data[2].extend([P1[2]])

    line1.set_xdata(link_data[0])
    line1.set_ydata(link_data[1])
    line1.set_3d_properties(link_data[2])

    # Joint point
    line2.set_xdata(joint_data[0])
    line2.set_ydata(joint_data[1])
    line2.set_3d_properties(joint_data[2])


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


def get_trans_mat(a, alpha, d, theta, return_P=False):
    """
    Obtain the transformation matrix from DH Parameters
    :param a: Link angle (in deg)
    :param alpha: Link twist
    :param d: Link offset (in deg)
    :param theta: Joint angle
    :param return_P: return the 3x1 translation matrix
    :return: transformation matrix and rotation matrix
    """
    if type(alpha) == int or type(alpha) == float:
        alpha = alpha*pi/180
    if type(theta) == int or type(theta) == float:
        theta = theta*pi/180

    R = rotation(alpha, 'x') * rotation(theta, 'z')
    R.simplify()
    T = add_translation(R, Matrix([a, -sin(alpha) * d, cos(alpha) * d, 1]))
    if return_P:
        return R, T, Matrix([a, -sin(alpha) * d, cos(alpha) * d])
    else:
        return R, T


def rotation(theta, direction):
    if direction == 'x':
        R = Matrix([[1, 0, 0],
                    [0, cos(theta), -sin(theta)],
                    [0, sin(theta), cos(theta)]])
    elif direction == 'y':
        R = Matrix([[cos(theta), 0, sin(theta)],
                    [0, 1, 0],
                    [-sin(theta), 0, cos(theta)]])
    elif direction == 'z':
        R = Matrix([[cos(theta), -sin(theta), 0],
                    [sin(theta), cos(theta), 0],
                    [0, 0, 1]])
    return R


def add_translation(R, t=Matrix([0, 0, 0, 1])):
    T = R.row_insert(len(R), Matrix([[0, 0, 0]]))
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
    display(symbols(info))


def matprint(matrix, alias=None):
    if alias:
        display(matrix.subs(alias))
    else:
        display(matrix)


def joint_print(joints, alias):
    for i in range(len(joints)):
        print('Joint %d position:' % (i+1))
        matprint(joints[i], alias)


def calc_blend_time(th, a, theta_0, theta_f):
    tb = th - np.sqrt(a**2*th**2 - a*(theta_f-theta_0))/a
    return tb


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


def calc_parabolic_traj(t, theta_0, theta_f, V, tb, a):
    """
    Linear and Parabolic Blended Trajectories
    """
    tf = t[-1]
    theta_vals = np.ndarray(np.shape(t))  # position
    theta_velo = np.ndarray(np.shape(t))  # velocity
    theta_acc = np.ndarray(np.shape(t))  # acceleration

    range1 = (t >= 0) & (t <= tb)
    theta_vals[range1] = theta_0 + V/(2*tb)*t[range1]**2
    theta_velo[range1] = V/tb*t[range1]
    theta_acc[range1] = V/tb

    range2 = (t > tb) & (t <= tf-tb)
    theta_vals[range2] = (theta_f+theta_0-V*tf)/2 + V*t[range2]
    theta_velo[range2] = V
    theta_acc[range2] = 0

    range3 = (t > tf-tb) & (t <= tf)
    theta_vals[range3] = theta_f - a*tf**2/2 + a*tf*t[range3] - a/2*t[range3]**2
    theta_velo[range3] = a*tf - a*t[range3]
    theta_acc[range3] = -a
    return theta_vals, theta_velo, theta_acc


