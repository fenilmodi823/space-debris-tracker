import numpy as np
import sys
import os

# Ensure we can import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_distance_km

def test():
    l1 = [1.0, 2.0, 3.0]
    l2 = [4.0, 5.0, 6.0]
    dist_l = calculate_distance_km(l1, l2)
    print(f"List distance: {dist_l}")

    a1 = np.array(l1)
    a2 = np.array(l2)
    dist_a = calculate_distance_km(a1, a2)
    print(f"Array distance: {dist_a}")

    assert abs(dist_l - dist_a) < 1e-9
    print("Test passed")

if __name__ == "__main__":
    test()
