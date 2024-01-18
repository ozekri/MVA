import abc
import functools
import math
from typing import Any, Callable, Dict, Optional, Tuple, Union

import jaxopt
import numpy as np

from ott.math import fixed_point_loop, matrix_square_root
from ott.math import utils as mu


import jax
import jax.numpy as jnp

import matplotlib.pyplot as plt

import ott
from ott.geometry import costs, pointcloud
from ott.problems.linear import linear_problem
from ott.solvers.linear import sinkhorn

from utils import plot_map, entropic_map


n_source = 30
n_target = 50
n_test = 10
p = 2

key = jax.random.PRNGKey(0)
keys = jax.random.split(key, 10)
x = jax.random.normal(keys[5], (n_source, p))

y0 = jax.random.normal(keys[7], (n_target // 2, p)) + jnp.array([5, 0])
y1 = jax.random.normal(keys[9], (n_target // 2, p)) + jnp.array([0, 8])
y = jnp.concatenate([y0, y1])


n_new = 10
x_new = jax.random.normal(keys[3], (n_new, p))

# jit first a Sinkhorn solver.
solver = jax.jit(sinkhorn.Sinkhorn())

gamma_list=[0.1,1.0,10.0,100.0]
for gamma in gamma_list:
    
    map_l1 = entropic_map(x, y, costs.Bdir(scaling_reg=gamma),solver)

    plot_map(x, y, x_new, map_l1(x_new))
    plt.xlim(-3,7)
    plt.show()