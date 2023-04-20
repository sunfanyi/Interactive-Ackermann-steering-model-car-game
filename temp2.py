# %%
import time
import numpy as np
import sympy as sp
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

from tools_kinematics import *

matplotlib.use('TkAgg')

# Constants
l0 = sp.symbols('l_0')
l2 = sp.symbols('l_2')
l3 = sp.symbols('l_3')
l4 = sp.symbols('l_4')
le = sp.symbols('l_e')
l0_val = 15
l2_val = 20
l3_val = 15
l4_val = 5
le_val = 10

# Variables
theta2 = sp.symbols(r"\theta_2")
theta3 = sp.symbols(r"\theta_3")
theta4 = sp.symbols(r"\theta_4")
d1 = sp.symbols('d_1')


# %%

R01, T01 = get_trans_mat(0, 0, l0 + d1, 0)
R12, T12 = get_trans_mat(0, 0, 0, theta2)
R23, T23 = get_trans_mat(l2, 90, 0, theta3 + sp.pi / 2)
R34, T34 = get_trans_mat(0, 90, l3, theta4)
R4e, T4e = get_trans_mat(-le, 0, l4, 0)

T04 = T01 * T12 * T23 * T34
T0e = T04 * T4e


#%% Inverse Kinematics to find  𝜃 values from the position metrices
def get_random_trans_mat():
    """
    Obtain random position metrices by applying forward kinematics using
    randomly assigned theta2, theta3, theta4 & d1 values.
    Random assignment is for proving concepts and is practically useless.
    """
    theta2_val = (np.random.rand() * 360 - 180) / 180 * np.pi
    theta3_val = (np.random.rand() * 180 - 90) / 180 * np.pi
    theta4_val = (np.random.rand() * 360 - 180) / 180 * np.pi
    d1_val = 5 + np.random.rand() * 35

    values = {l0: l0_val, l2: l2_val, l3: l3_val, l4: l4_val, le: le_val,
              theta2: theta2_val, theta3: theta3_val, theta4: theta4_val,
              d1: d1_val}
    T0e_target = T0e.subs(values)
    # convert infinitely small non-zero float to zero
    T0e_target = np.array(T0e_target, dtype=np.float32)
    T0e_target[np.abs(T0e_target) < 1e-7] = 0

    return T0e_target


r11 = sp.symbols('r_{11}')
r12 = sp.symbols('r_{12}')
r13 = sp.symbols('r_{13}')
r21 = sp.symbols('r_{21}')
r22 = sp.symbols('r_{22}')
r23 = sp.symbols('r_{23}')
r31 = sp.symbols('r_{31}')
r32 = sp.symbols('r_{32}')
r33 = sp.symbols('r_{33}')
X = sp.symbols('X')
Y = sp.symbols('Y')
Z = sp.symbols('Z')
empty_vals = {r11: None, r12: None, r13: None,
              r21: None, r22: None, r23: None,
              r31: None, r32: None, r33: None,
              X: None, Y: None, Z: None}


def solve_inverse_kinematics(vals_target):
    # ========================= d1 ==============================
    d1_inv = le * r31 - l4 * r33 + Z - l0 - l3 * r33
    d1_ans = float(d1_inv.subs(vals_target))

    # ========================= theta2 ==========================
    theta2_inv = sp.atan2((le * r21 - r23 * (l3 + l4) + Y) / l2, (le * r11 - r13 * (l3 + l4) + X) / l2)
    theta2_ans = float(theta2_inv.subs(vals_target))

    # ========================= theta3 ==========================
    if sp.sin(theta2_ans) != 0:
        theta3_inv = sp.atan2(r33, r23 / sp.sin(theta2_ans))
    else:
        theta3_inv = sp.atan2(r33, r13 / sp.cos(theta2_ans))

    theta3_ans = float(theta3_inv.subs(vals_target))
    # theta3 range from -180 to 180 deg
    if theta3_ans > np.pi:
        theta3_ans -= 2 * np.pi

    # ========================= theta4 ==========================
    if theta3_ans == np.pi / 2:
        theta4_inv = sp.atan2(r12, -r11) - theta2_ans
    elif theta3_ans == -np.pi / 2:
        theta4_inv = sp.atan2(-r12, r11) + theta2_ans
    else:
        theta4_inv = sp.atan2(-r32 / sp.cos(theta3_ans), r31 / sp.cos(theta3_ans))

    theta4_ans = float(theta4_inv.subs(vals_target))
    # theta4 range from -180 to 180 deg
    if theta4_ans > np.pi:
        theta4_ans -= 2 * np.pi

    return d1_ans, theta2_ans, theta3_ans, theta4_ans


num_via_points = 10

# + 2 because start and end points:
d1_points = np.ndarray((num_via_points + 2,))
theta2_points = np.ndarray((num_via_points + 2,))
theta3_points = np.ndarray((num_via_points + 2,))
theta4_points = np.ndarray((num_via_points + 2,))

# XYZ values for target positions:
P_coordinates = np.ndarray([num_via_points + 2, 3])

for i in range(num_via_points + 2):
    P = get_random_trans_mat()
    P_coordinates[i, :] = P[:3, -1]
    # get rii, X, Y, Z
    vals_target = update_target_vals(P, empty_vals)
    vals_target.update({l0: l0_val, l2: l2_val, l3: l3_val, l4: l4_val, le: le_val})

    # solve theta values
    d1_points[i], theta2_points[i], theta3_points[i], theta4_points[i] = \
        solve_inverse_kinematics(vals_target)


# %%
# Now we have arrays for each theta, each array has a length of 12, corresponding to 12 points.
# The next step is to solve  𝑎,  𝑉,  𝑡𝑏𝑙𝑒𝑛d and  𝑡𝑙𝑖𝑛𝑒𝑎𝑟.

def calc_kinematics_parameters(via_points, tf):
    a_mins = np.ndarray((num_via_points + 2,))  # minimum required accelerations
    a_vals = np.ndarray((num_via_points + 2,))  # actual acclerations
    V_vals = np.ndarray((num_via_points + 1,))  # velocity for linear regions
    t_blends = np.ndarray((num_via_points + 2,))  # time for blend regions
    t_linears = np.ndarray((num_via_points + 1,))  # time for linear regions

    a_mins[0] = np.abs(8 * (via_points[1] - via_points[0]) / (3 * tf[0] ** 2))
    a_mins[-1] = np.abs(8 * (via_points[-1] - via_points[-2]) / (3 * tf[-1] ** 2))

    # for the middle segments:
    left = ((via_points[2:] - via_points[1:-1]) / tf[1:] - (via_points[1:-1] - via_points[:-2]) / tf[:-1]) / tf[:-1]
    right = ((via_points[2:] - via_points[1:-1]) / tf[1:] - (via_points[1:-1] - via_points[:-2]) / tf[:-1]) / tf[1:]
    a_mins[1:-1] = np.maximum(np.abs(left), np.abs(right))
    a_mins = 2 * a_mins

    # Step 1: Find the start and end acceleration:
    a_vals[0] = np.sign(via_points[1] - via_points[0]) * a_mins[0]
    a_vals[-1] = np.sign(via_points[-2] - via_points[-1]) * a_mins[-1]

    # Step 2: Find the start and end blend times (using a_vals[0] and a_vals[-1]):
    t_blends[0] = tf[0] - np.sqrt(tf[0] ** 2 - 2 * (via_points[1] - via_points[0]) / a_vals[0])
    t_blends[-1] = tf[-1] - np.sqrt(tf[-1] ** 2 + 2 * (via_points[-1] - via_points[-2]) / a_vals[-1])

    # Step3: Find the start and end velocity (using t_blends[0] and t_blends[-1]):
    V_vals[0] = (via_points[1] - via_points[0]) / (tf[0] - 0.5 * t_blends[0])
    V_vals[-1] = (via_points[-1] - via_points[-2]) / (tf[-1] - 0.5 * t_blends[-1])

    # Step 4: Find middle via points velocity at linear regions:
    V_vals[1:-1] = (via_points[2:-1] - via_points[1:-2]) / tf[1:-1]

    # Step 5: Find middle via points blend acceleration (using V_vals[:]):
    a_vals[1:-1] = np.sign(V_vals[1:] - V_vals[:-1]) * a_mins[1:-1]

    # Step 6: Find middle via points blend times (using V_vals[:] and a_vals[1:-1]):
    t_blends[1:-1] = (V_vals[1:] - V_vals[:-1]) / a_vals[1:-1]

    # Step 6: Find all times for linear regions (using t_blends[:]):
    t_linears[0] = tf[0] - t_blends[0] - 0.5 * t_blends[1]
    t_linears[-1] = tf[-1] - t_blends[-1] - 0.5 * t_blends[-2]
    t_linears[1:-1] = tf[1:-1] - 0.5 * t_blends[2:-1] - 0.5 * t_blends[1:-2]

    return a_vals, V_vals, t_blends, t_linears


# calculate distance between two points position
dist = np.sqrt(np.sum((P_coordinates[1:] - P_coordinates[:-1]) ** 2, axis=1))
t_tot = 25  # total time: 25 s
# time between two points depending on the distance
tf = dist / np.sum(dist) * t_tot
print('tf:', tf)

a_vals_d1, V_vals_d1, b_blends_d1, t_linears_d1 = calc_kinematics_parameters(d1_points, tf)

a_vals_theta2, V_vals_theta2, b_blends_theta2, t_linears_theta2 = calc_kinematics_parameters(theta2_points, tf)

a_vals_theta3, V_vals_theta3, b_blends_theta3, t_linears_theta3 = calc_kinematics_parameters(theta3_points, tf)

a_vals_theta4, V_vals_theta4, b_blends_theta4, t_linears_theta4 = calc_kinematics_parameters(theta4_points, tf)


# %%
def get_trajectory(via_points, tf, a_vals, V_vals, t_blends,
                   resolution=1000):
    # for the whole trajectory
    time_history = []
    disp_history = []
    velo_history = []
    acc_history = []
    disp_ideal_history = []
    t_start = 0

    # initialise starting values
    disp_last = via_points[0]
    velo_last = 0

    # For each segment:
    for i in range(num_via_points + 1):
        t_local = np.linspace(0, tf[i], resolution)
        tb_left = t_blends[i] if i == 0 else t_blends[i] / 2
        tb_right = t_blends[i + 1] if i == num_via_points else t_blends[i + 1] / 2
        disp, velo, acc, disp_ideal = calc_parabolic_traj_via_points(t_local, disp_last, velo_last,
                                                                     V_vals[i], a_vals[i],
                                                                     a_vals[i + 1], tb_left, tb_right)
        # use last points as the initial points for the next segment
        disp_last = disp[-1]
        velo_last = velo[-1]

        time_history.extend((t_local + t_start).tolist())

        disp_history.extend(disp.tolist())
        velo_history.extend(velo.tolist())
        acc_history.extend(acc.tolist())
        disp_ideal_history.extend(disp_ideal.tolist())

        t_start += tf[i]

    return time_history, disp_history


# %% animation
res = 10
_, d1_paths = get_trajectory(d1_points, tf, a_vals_d1, V_vals_d1, b_blends_d1,
                             resolution=res)
_, theta2_paths = get_trajectory(theta2_points, tf, a_vals_theta2, V_vals_theta2, b_blends_theta2,
                                 resolution=res)
_, theta3_paths = get_trajectory(theta3_points, tf, a_vals_theta3, V_vals_theta3, b_blends_theta3,
                                 resolution=res)
_, theta4_paths = get_trajectory(theta4_points, tf, a_vals_theta4, V_vals_theta4, b_blends_theta4,
                                 resolution=res)

# Get the Position of end effector in frame 0
Pee = sp.Matrix([0, 0, 0, 1])
P0e = T0e * Pee

fig = plt.figure(figsize=[8, 6])
ax = fig.add_subplot(projection='3d')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
x_max = l2_val + l3_val + l4_val
z_max = 40 + l0_val + le_val
ax.set_xlim([-x_max * 1, x_max * 1])
ax.set_ylim([-x_max * 1, x_max * 1])
ax.set_zlim([-z_max * 1, z_max * 1])

line1, = ax.plot([0], [0], [0], 'r.')  # end effector
line2, = ax.plot([0], [0], [0], 'b-')  # link
line3, = ax.plot([0], [0], [0], 'bx')  # joint
line4, = ax.plot([P_coordinates[0, 0]], [P_coordinates[0, 1]], [P_coordinates[0, 2]], 'gx')  # via points

end_memory = []  # show end effector history

for i in range(len(d1_paths)):
    d1_val = d1_paths[i]
    theta2_val = theta2_paths[i]
    theta3_val = theta3_paths[i]
    theta4_val = theta4_paths[i]
    values = {l0: l0_val, l2: l2_val, l3: l3_val, l4: l4_val, le: le_val,
              theta2: theta2_val, theta3: theta3_val, theta4: theta4_val,
              d1: d1_val}
    end_pos = P0e.subs(values)

    if len(end_memory) < 20:
        end_memory.append(end_pos[:3])
    else:
        end_memory = end_memory[1:] + [end_pos[:3]]

    line1.set_xdata([i[0] for i in end_memory])
    line1.set_ydata([i[1] for i in end_memory])
    line1.set_3d_properties([i[2] for i in end_memory])

    Pii_pos = sp.Matrix([0, 0, 0, 1])
    P01_pos = (T01 * Pii_pos).subs(values)
    P02_pos = (T01 * T12 * Pii_pos).subs(values)
    P03_pos = (T01 * T12 * T23 * Pii_pos).subs(values)
    P04_pos = (T01 * T12 * T23 * T34 * Pii_pos).subs(values)

    plot_links_moving(line2, line3, [Pii_pos, P01_pos, P02_pos, P03_pos, P04_pos, end_pos])

    # plot via points
    line4.set_xdata(P_coordinates[i // res:i // res + 2, 0])
    line4.set_ydata(P_coordinates[i // res:i // res + 2, 1])
    line4.set_3d_properties(P_coordinates[i // res:i // res + 2, 2])

    fig.suptitle('$d_1: %.2f, \\theta_2: %.1f^o, \\theta_3: %.1f^o, \
                 \\theta_4: %.1f^o$' % (
    d1_val, theta2_val / sp.pi * 180, theta3_val / sp.pi * 180, theta4_val / sp.pi * 180))
    fig.canvas.draw()
    fig.canvas.flush_events()
    # time.sleep(0.1)
plt.show()
