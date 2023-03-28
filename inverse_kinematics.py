# -*- coding: utf-8 -*-
# @File    : inverse_kinematics.py
# @Time    : 28/03/2023
# @Author  : Fanyi Sun
# @Github  : https://github.com/sunfanyi
# @Software: PyCharm

import numpy as np
from math import sin, cos, tan, atan2, sqrt, pi

from game_function import rotation


def calc_inverse(car):
    """
    Specifically designed for Car class, to perform inverse kinematics.
    """
    A = car.length
    B = car.width
    C = car.height
    r = car.wheel_radius
    l = car.wheel_base

    theta = car.car_orientation
    psi = car.steering_angle
    V = car.car_speed
    psi_dot = car.steering_rate
    mat_input = np.array([V, psi_dot])
    mat_input_to_speed = np.array([[cos(theta), 0],
                                   [sin(theta), 0],
                                   [1 / l * tan(psi), 0],
                                   [0, 1]])
    # Velocity metrix in global frame
    car.P_i_dot = np.matmul(mat_input_to_speed, mat_input)
    theta_dot = car.P_i_dot[2]

    # calculate rear wheels angular velocities
    RI0 = rotation(theta, 'z')
    R0I = RI0.T
    alpha = sqrt(B**2 + 4*l**2) / (2*r * sqrt(1+(4*l**2)/B**2))
    mat_inverse = np.array([[1/r, 0, - alpha],
                            [1/r, 0, alpha]])
    vel_RL, vel_RR = np.matmul(mat_inverse, np.matmul(R0I, car.P_i_dot[:3]))

    if vel_RL != vel_RR:  # suppress divided by zero warning
        # calculate instantaneous center of rotation
        R = B/2 * ((vel_RL + vel_RR) / (vel_RL - vel_RR))

        # calculate front wheels orientations
        beta_FL = - atan2(l, R + B/2)
        beta_FR = - atan2(l, R - B/2)

        # calculate front wheels angular velocities
        vel_FL = theta_dot * sqrt(l**2 + (R + B/2)**2) / r
        vel_FR = theta_dot * sqrt(l**2 + (R - B/2)**2) / r
    else:
        R = np.nan
        beta_FL = 0
        beta_FR = 0
        vel_FL = 0
        vel_FR = 0

    # update car kinematics
    car.ICR = R
    car.wheels_orientation = np.float32([beta_FL, beta_FR, 0, 0])
    car.wheels_speed = np.float32([vel_FL, vel_FR, vel_RL, vel_RR])


