import numpy as np
import heapq

WEIGHTS = {
  's_gr_01_01': 0.5 * 15,
  's_gr_01_02': 0.1 * 15,
  's_gr_01_03': 0.4 * 15,
  's_gr_2_1': 0.4 * 15,
  's_gr_2_2': 0.4 * 15,
  's_gr_2_3': 0.1 * 15,
  's_gr_2_4': 0.1 * 15,
  's_gr_3_1': 0.25 * 15,
  's_gr_3_2': 0.25 * 15,
  's_gr_3_3': 0.1 * 15,
  's_gr_3_4': 0.15 * 15,
  's_gr_3_5': 0.15 * 15,
  's_gr_3_6': 0.1 * 15,
  's_gr_4_1': 0.5 * 15,
  's_gr_4_2': 0.2 * 15,
  's_gr_4_3': 0.3 * 15,
  's_gr_5_1': 0.5 * 15,
  's_gr_5_2': 0.5 * 15,
  's_gr_6_1': 0.1 * 6,
  's_gr_6_2': 0.1 * 6,
  's_gr_6_3': 0.1 * 6,
  's_gr_6_4': 0.1 * 6,
  's_gr_6_5': 0.3 * 6,
  's_gr_6_6': 0.1 * 6,
  's_gr_6_7': 0.1 * 6,
  's_gr_6_8': 0.1 * 6,
  's_gr_7_1': 0.1 * 10,
  's_gr_7_2': 0.1 * 10,
  's_gr_7_3': 0.1 * 10,
  's_gr_7_4': 0.1 * 10,
  's_gr_7_5': 0.2 * 10,
  's_gr_7_6': 0.1 * 10,
  's_gr_7_7': 0.2 * 10,
  's_gr_7_8': 0.1 * 10,
  's_gr_8_01': 0.04 * 9,
  's_gr_8_02': 0.08 * 9,
  's_gr_8_03': 0.04 * 9,
  's_gr_8_04': 0.1 * 9,
  's_gr_8_05': 0.1 * 9,
  's_gr_8_06': 0.05 * 9,
  's_gr_8_07': 0.1 * 9,
  's_gr_8_08': 0.05 * 9,
  's_gr_8_09': 0.05 * 9,
  's_gr_8_10': 0.04 * 9,
  's_gr_8_11': 0.05 * 9,
  's_gr_8_12': 0.1 * 9,
  's_gr_8_13': 0.1 * 9,
  's_gr_8_14': 0.05 * 9,
  's_gr_8_15': 0.05 * 9,
}

def compute_accessibility_index(proximity_dict, max_distance=1000, k=100, max_amenities=3, f=0.5, weights_dict=WEIGHTS):
    # f determines the rate at which the value of having additional amenities diminishes
    # small f (0.1, 0.5) modest increase in score with additional amenities
    # moderate f (0.5, 1) noticeable increase in score with additional amenities
    # large f (1, +) a steep increase in the score with more amenities
    def normalize_distance(distance, max_distance, k):
        # This also provides diminishing returns as distance increases.
        # k is a parameter controlling the rate of decrease in accessibility beyond half of the maximum distance
        # small k (50, 150) distances close to max_distance will drop off quickly, but distances near half of max_distance will still have a relatively high score
        # moderate k (150, 300) a more gradual penalty for greater distances from falf max_distance to max_distance
        # larger k (300, 500) when nearing max_dictance we still have a noticeable contribution to the score
        # exp ensures that distances become increasingly less accessible as they grow beyond a certain point
        if distance <= max_distance / 2:
            return 1
        elif distance <= max_distance:
            return np.exp(-(distance - max_distance / 2) / k)
        else:
            return 0
    
    def diminishing_returns(count, max_amenities, f):
        if count <= 1:
            return 1
        elif count <= max_amenities:
            return 1 + (count - 1) * f
        else:
            return 1 + (max_amenities - 1) * f
    
    total_score = 0
    total_weight = 0
    max_possible_score = 0

    for subgroup, distances in proximity_dict.items():
        weight = weights_dict.get(subgroup)
        max_possible_score += weight * diminishing_returns(max_amenities, max_amenities, f)

        # We need to consider only the closest max_amenities number
        num_amenities = len(distances)
        distances = heapq.nsmallest(max_amenities, distances)

        normalized_scores = [normalize_distance(d, max_distance, k) for d in distances]
        avg_score = np.mean(normalized_scores) * diminishing_returns(num_amenities, max_amenities, f)
        
        weighted_score = avg_score * weight
        total_score += weighted_score
        total_weight += weight
        
    if total_weight == 0:
        return 0

    return round((total_score / max_possible_score) * 100, 2)
