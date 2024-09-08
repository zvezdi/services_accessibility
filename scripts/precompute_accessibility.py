import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from service_accessibility.services.precompute_accessibility import compute_and_store_accessibility

if __name__ == "__main__":
    length_type = 'length_m'
    max_distance = 1000
    k = 300
    max_amenities = 1
    f = 0.5

    compute_and_store_accessibility(length_type, max_distance, k, max_amenities, f, recompute=True)
