import random

def predict_defect_probability(file_stats):
    """
    Mock defect predictor that returns a probability based on file statistics.
    If we had scikit-learn working, this would use a Random Forest model.
    """
    base_prob = 0.1
    if file_stats.get('churn', 0) > 10:
        base_prob += 0.3
    if file_stats.get('complexity', 0) > 15:
        base_prob += 0.4
    
    # Add a bit of jitter
    prob = base_prob + random.uniform(-0.05, 0.05)
    return min(max(prob, 0.0), 0.99)
