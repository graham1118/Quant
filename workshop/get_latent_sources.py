import requests
import time
import pandas as pd
import numpy as np
from functions import *

def compute_sources():
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #Load Historical Data
    with open('stream_data.txt', 'r') as f:
        prices = []
        v_bid = []
        v_ask = []
        for i in f.readlines()[-2200:]:
            prices.append(round(float(i.strip().split(',')[1]), 2))
            v_bid.append(round(float(i.strip().split(',')[2]), 3))
            v_ask.append(round(float(i.strip().split(',')[-1]), 3))
        f.close()


    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Split Historical Data into 3 segments
    [prices1, prices2, prices3] = np.array_split(prices, 3)
    [v_bid1, v_bid2, v_bid3] = np.array_split(v_bid, 3)
    [v_ask1, v_ask2, v_ask3] = np.array_split(v_ask, 3)
    
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Generate timeseries and calculate sources
    timeseries180, timeseries360, timeseries720 = generate_timeseries(prices1, 180), generate_timeseries(prices1, 360), generate_timeseries(prices1, 720)
    centers180, centers360, centers720 = find_cluster_centers(timeseries180, 100), find_cluster_centers(timeseries360, 100), find_cluster_centers(timeseries720, 100)
    s1, s2, s3 = choose_effective_centers(centers180, 20), choose_effective_centers(centers360, 20), choose_effective_centers(centers720, 20)

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Use the second time period to generate the independent and dependent
    Dpi_r, Dp = linear_regression_vars(prices2, v_bid2, v_ask2, s1, s2, s3) # Δp = w0 + w1 * Δp1 + w2 * Δp2 + w3 * Δp3 + w4 * r.

    w = find_parameters_w(Dpi_r, Dp)                                        # Find w = [w0, w1, w2, w3, w4]
                                                                            #len(prices2) - len(Dp) == 721
    f = open('latent_data.py', 'w')
    f.write(f's1 = {repr(s1)}\ns2 = {repr(s2)}\ns3 = {repr(s3)}\nw = {repr(w)}\n')
    f.close()

    return prices3, v_bid3, v_ask3, s1, s2, s3, w

prices3, v_bid3, v_ask3, s1, s2, s3, w = compute_sources()
dps = predict_dps(prices3, v_bid3, v_ask3, s1, s2, s3, w)               # Predict average price changes over the third time period.
bank_balance = evaluate_performance(prices3, dps, t=1.2, step=1)        # Evaluate Bot Performance given delta_prices    |     2 steps is every 20s
print(bank_balance)