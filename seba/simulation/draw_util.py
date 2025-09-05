import numpy as np
import scipy as sp

def draw_circle(matrix, center, radius=1, tag=1, invert=False):
    shape = matrix.shape
    x, y = np.ogrid[:shape[0], :shape[1]]
    distance_sq = (x - center[0])**2 + (y - center[1])**2 
    if not invert:
        matrix[(distance_sq <= radius**2)] = tag
    else:
        matrix[(distance_sq > radius**2)] = tag
    return matrix
