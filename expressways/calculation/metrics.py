import pandas as pd
import numpy as np
import datetime

def weighted_quantile(values, quantiles, sample_weight=None, values_sorted=False, old_style=True):
    """ Very close to numpy.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: numpy.array with data
    :param quantiles: array-like with many quantiles needed
    :param sample_weight: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of initial array
    :param old_style: if True, will correct output to be consistent with numpy.percentile.
    :return: numpy.array with computed quantiles.
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    sample_weight = np.array(sample_weight)
    assert np.all(quantiles >= 0) and np.all(quantiles <= 1), 'quantiles should be in [0, 1]'

    if not values_sorted:
        sorter = np.argsort(values)
        values = values[sorter]
        sample_weight = sample_weight[sorter]
    # the last term is to calculate the center of the bin
    weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
    if old_style:
        # To be convenient with numpy.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= np.sum(sample_weight)
    return np.interp(quantiles, weighted_quantiles, values)

def get_data_on_time_range(df):
    """
    Retrieve from data frame only rows within specified time range
    """
    time_start = datetime.datetime.strptime('06:00:00', '%H:%M:%S')
    time_end = datetime.datetime.strptime('20:00:00', '%H:%M:%S')

    valid_df = df.loc[(df['Departure Time (HH:MM:SS)'] > time_start) & (df['Departure Time (HH:MM:SS)'] < time_end)]
    return valid_df

def incidents_cleared(incident_list):
    """
    Sum of filtered incidents' frequency that are last less than an hour and divide them by the sum of all filtered incidents' frequency.

    Filtered means only those that has incidents cleared checked and excluding low flow
    """
    filtered_list = []
    less_than_hour_list = []

    for incident in incident_list:
        if incident['flow'] != 'Low' and incident['incidents_cleared']:
            filtered_list.append(incident['frequency'])
            if incident['duration'] <= 60:
                less_than_hour_list.append(incident['frequency'])

    if (len(filtered_list) > 0):
        return 100 * (sum(less_than_hour_list) / sum(filtered_list))
    else:
        return 0
    
def pti(df):
    """
    The ratio of the 95th percentile journey time of all journeys and the free-flow journey time.

    Planning Time Index = [Planning Time] / [Free-flow journey time] 
    :param df: Dataframe of model data
    """
    free_flow = df['Time Taken (s)'].loc[df['Vehicle Type'] == 1].quantile(0.15)
    np_data = np.array(df[['Time Taken (s)', "Flows"]])
    planning_time = weighted_quantile(np_data[:, 0], 0.95, sample_weight=np_data[:, 1])  # 0.95 the 95th percentile
    return planning_time / free_flow

def acceptable_journeys(df):
    """
    Proportion of journeys faster than 4/3 of the free flow journey time.  

    Proportion of acceptable journeys = [Traffic Faster than 4/3 journey time] / [all traffic]  
    :param df: Dataframe of model data
    """
    free_flow = df['Time Taken (s)'].loc[df['Vehicle Type'] == 1].quantile(0.15)
    faster_ff = df['Time Taken (s)'].loc[df['Vehicle Type'] == 1][df['Time Taken (s)'] < (4 / 3) * free_flow].count()
    return (100 * faster_ff / df['Time Taken (s)'].loc[df['Vehicle Type'] == 1].count())

def average_speed(df):
    """
    The flow weighted average speed of car journeys.

    Average speed = Sum over all 15 minute periods (link length * flow)/ Sum over all 15 minute periods (15 minute average speed*flow) 
    :param df: Dataframe of model data
    """
    mean15min = df.groupby(pd.Grouper(key='Departure Time (HH:MM:SS)', freq='15min')).mean()
    return 3.6 * ((mean15min['Distance (m)'] * mean15min['Flows']).sum() / (
                mean15min['Time Taken (s)'] * mean15min['Flows']).sum())
