import numpy as np

def select_data(data, name=""):
    return data.loc[:, (slice(None), name)].values

def neturalize_weights(weights):
    # 計算mean或std要把na值排除
    numerator = (weights - np.mean(weights[~np.isnan(weights)]))
    denominator = np.std(weights[~np.isnan(weights)])
    return numerator/denominator