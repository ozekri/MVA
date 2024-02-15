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

print(x)

plot_map(x, y)
plt.show()

n_new = 10
x_new = jax.random.normal(keys[3], (n_new, p))

# jit first a Sinkhorn solver.
solver = jax.jit(sinkhorn.Sinkhorn())

map = entropic_map(x, y, costs.SqEuclidean(),solver)

plot_map(x, y, x_new, map(x_new))
plt.show()