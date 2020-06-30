import pandas as pd
import numpy as np
from functools import reduce
import os


def load_xl_model(df, path):
    """
    Load a excel file from a path and return a dataframe
    :param path: path as str to the desired filename
    :return df: dataframe with the loaded data
    """

    if df.empty:
        del df
        df = pd.read_excel(path, usecols='F,G,I,L,O')
    else:
        df = df.append(pd.read_excel(path, usecols='F,G,I,L,O'), ignore_index=True)
    return df


def load_csv_model(df, path, flow):
    """
    Load a excel file from a path and return a dataframe
    :param path: path as str to the desired filename
    :return df: dataframe with the loaded data
    """

    if df.empty:
        del df
        df = pd.read_csv(path, usecols=[5, 6, 8, 11, 14])
        df['Flows'] = int(flow)
    else:
        df_temp = pd.read_csv(path, usecols=[5, 6, 8, 11, 14])
        df_temp['Flows'] = int(flow)
        df = df.append(df_temp, ignore_index=True)
    return df


def load_csv_model_freq(df, path, flow, freq):
    """
    Load a excel file from a path and return a dataframe
    :param path: path as str to the desired filename
    :param freq: frequency of the model
    :return df: dataframe with the loaded data
    """
    if df.empty:
        del df
        df_temp = pd.read_csv(path, header = 0, skiprows=lambda i: i % 5 != 0)
        df_temp['Departure Time (HH:MM:SS)'] = pd.to_datetime(df_temp['Departure Time (HH:MM:SS)'], format='%H:%M:%S')
        df = pd.DataFrame(np.repeat(df_temp.values, freq, axis=0))
        df.columns = df_temp.columns
        df['Distance (m)'] = pd.to_numeric(df['Distance (m)'])
        df['Flows'] = pd.to_numeric(df['Flows'])
        df['Speed'] = pd.to_numeric(df['Speed'])
        df['Time Taken (s)'] = pd.to_numeric(df['Time Taken (s)'])
        df['Vehicle Type'] = pd.to_numeric(df['Vehicle Type'])
    else:
        df_temp = pd.read_csv(path, skiprows=lambda i: i % 5 != 0)
        df_temp['Departure Time (HH:MM:SS)'] = pd.to_datetime(df_temp['Departure Time (HH:MM:SS)'], format='%H:%M:%S')
        df_temp_freq = pd.DataFrame(np.repeat(df_temp.values, freq, axis=0))
        df_temp_freq.columns = df_temp.columns
        df_temp_freq['Distance (m)'] = pd.to_numeric(df_temp_freq['Distance (m)'])
        df_temp_freq['Flows'] = pd.to_numeric(df_temp_freq['Flows'])
        df_temp_freq['Speed'] = pd.to_numeric(df_temp_freq['Speed'])
        df_temp_freq['Time Taken (s)'] = pd.to_numeric(df_temp_freq['Time Taken (s)'])
        df_temp_freq['Vehicle Type'] = pd.to_numeric(df_temp_freq['Vehicle Type'])
        df = df.append(df_temp_freq, ignore_index=True)
    return df


def load_header_data(folder, filetype):
    """
    Load information about the models from filenames
    :param folder: dataframe with the loaded data
    :return header: Header information about the data source
    """
    header = []
    for file in os.listdir(folder):
        if file.endswith('.' + filetype):
            header.append(os.path.splitext(file)[0].split())
            header[-1].insert(0, file)
    header_df = pd.DataFrame(header, columns=['Filename', 'Flow', 'Speed', 'LaneBlockage', 'Duration'])
    return header_df


def save_data_hdf5(filename, df):
    """
    :param filename: file to save/append data in
    :param df: Dataframe with model data
    :return:
    """

    df.to_hdf(os.path.join('datafile', filename + '.h5'), key='df', mode='w')

    return


def load_data_hdf5(df, path):
    """
    :param filename: file to save/append data in
    :param df: Dataframe with model data
    :return:
    """

    if df.empty:
        del df
        df = pd.read_hdf(path)
    else:
        df = pd.read_hdf(path)
    return df


def query_data(header, params):
    """
    Get the filename of the dataset based on input parameters
    :param header: Header information about the data source
    :param params: Parameters for model selection
    :return filename as str
    """
    param_names = ['Flow', 'LaneBlockage', 'Duration']
    for i in range(len(params)):
        header = header.loc[header[param_names[i]] == params[i]]
        
    return header['Filename'].iloc[0]


def GCD(a, b):
    """
    Greatest common divider the Euclidean way
    :param a,b: two integers
    """
    if b == 0:
        return a
    else:
        return GCD(b, a % b)


def norm_freqs(freq_list):
    """
    Normalise the frequencies by dividing with the greatest common divider of the frequencies
    We can then achieve less copies of the same models in the final model without affecting the statistical measures
    :param freq_list: a list with the frequencies of the models
    :return: a normalised version of the input
    """
    # Recursively pick the items of the list and calculate the GCD
    gcd_value = reduce(GCD, freq_list)
    # normalise the items of the list by dividing with the GCD
    return [int(x / gcd_value) for x in freq_list]


def frequency_change(freq_list, change_perc):
    """
    Function to apply percentage change on frequencies for expressways objects
    :param freq_list: a list with the frequencies of the models
    :param change_perc: a list with the percentages that the frequencies should change
    :return:a list with the transformed frequencies of the models
    """
    return [int(freq + (change_perc[i] * freq)) for i, freq in enumerate(freq_list)]


def duration_bin(freq_list, change_perc, durations):
    """
    Perform a frequency transform based on the percentages that affect the durations from the design components.
    We split the frequency change to its decimal and integer part and cascade the decimal part to smaller durations by
    scaling it according the ratios between durations.
    :param freq_list: a list with the frequencies of the models
    :param change_perc: a list with the percentages that the durations should change
    :param: list of all available durations
    :return: a list with the transformed frequencies of the models
    """

    # Calculate the ratio between the durations starting from the last (largest) to the first (smallest)
    times_rel = [0] * len(durations)
    times_rel[len(durations) - 1] = 1
    for i in range(len(durations) - 1, 0, -1):
        times_rel[i - 1] = durations[i] / durations[i - 1]

    # Split the change percentages in two lists based on their sign
    incr_perc = []
    reduct_perc = []
    for i in change_perc:
        if i > 0:
            incr_perc.append(i)
            reduct_perc.append(0)
        elif i < 0:
            incr_perc.append(0)
            reduct_perc.append(i)
        else:
            incr_perc.append(0)
            reduct_perc.append(0)

    # Negative changes (reduction): Iteratively we calculate the decrease for each of the duration bins.
    # We first split the floats in their integer and decimal part. We keep the decimal part and propagate the decimal
    # part by scaling it with the relative ratio above. Finally we should have a list of integers (apart from the first
    # list item) that represent the frequency that should be reduced from the initial frequencies

    reduct = [a * abs(b) for a, b in zip(freq_list, reduct_perc)]

    for i in range(len(reduct) - 1, 0, -1):
        i_part = int(reduct[i] // 1)
        d_part = float("{0:.4f}".format(reduct[i] - i_part))
        d_part_new = d_part * times_rel[i - 1]
        reduct[i] = i_part
        reduct[i - 1] = reduct[i - 1] + d_part_new
    # Same as above for percentage increases
    incr = [a * b for a, b in zip(freq_list, incr_perc)]

    for i in range(len(incr) - 1, 0, -1):
        i_part = int(incr[i] // 1)
        d_part = float("{0:.4f}".format(incr[i] - i_part))
        d_part_new = d_part * times_rel[i - 1]
        incr[i] = i_part
        incr[i - 1] = incr[i - 1] + d_part_new
    # Merge the positive and negative changes for the above percentages and round them (for the first items of the list)
    # Then return the updated frequencies list.
    final_change = [int(round(a - b)) for a, b in zip(incr, reduct)]
    return [(a + b) for a, b in zip(freq_list, final_change)]
