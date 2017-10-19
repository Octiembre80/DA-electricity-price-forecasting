"""Functions used for multi-dimensional weather data manipulation"""

import datetime as dt
import numpy as np
import pandas as pd
import os
from functools import reduce


def prepare_training_data(months=range(1, 13, 1), inputs=['SWDIFDS_RAD', 'SWDIRS_RAD'], return_index=True, 
                         base_path='./processed_data/weather', scale=True):
    
    """Load specified weather variables and their respective timeseries indices from .npy/.txt files. Scale
    each variable to 0-1 range by dividing by the maximum observed value. Return final data tensors and indices
    as dictonary with key=variable_name. Each tensor will contain all data samples for a specific variable."""
    
    indices = {}
    tensors = {}
    
    for variable in inputs:
        
        index_arr = []
        data_arr = []
        amax = 0

        for month in months:
            
            # define filenames
            date = dt.date(2015, month, 1).strftime('%Y%m')
            filename = os.path.join(base_path, '{}.2D.{}'.format(variable, date))
            
            # load index of datafile from .txt file
            index_arr.append(pd.read_csv('{}.txt'.format(filename), parse_dates=True, header=None, index_col=0))
            
            # load data for current month
            data = np.load('{}.npy'.format(filename))
            
            # get maximum value
            max_val = np.amax(data)
            
            # check if new maximum value was found
            if scale:
                amax = max(amax, max_val)
            
            # append month data to current variable tensor
            data_arr.append(data)
        
        # scale data by global maximum of current variable
        if scale:
            data_arr /= amax

        indices[variable] = pd.concat(index_arr).index
        
        # form one big array from monthly subsets
        tensors[variable] = np.vstack(data_arr)

    if return_index:
        return indices, tensors
    else:
        return tensors
    

def check_indices(indices):
    
    """Calculate the union of all provided indices.
    Check if any index has missing values compared to that union."""
    
    missing = dict([(key, None) for key in indices.keys()])
    
    # caclulate union of indices
    common_index = reduce(lambda  left,right: left.join(right, how='outer'), indices.values())
    
    # check if union contains entries that are not present in a particular index
    for key, val in indices.items():
        missing[key] = common_index.difference(val)
        
    return missing


def align_transform_data(labels, feature_dict, variables, scaler, index):
    
    """Clean feature arrays of samples that are missing in a given set of labels. Scale
    label data. Stack all features in one feature array by merging on third dimension."""
    
    assert all((len(labels) == len(feature) for feature in feature_dict.values()))
    
    # find NaN values in label dataset
    mask = labels.isnull().values
    
    # drop NaN entries in label dataset
    labels.dropna(inplace=True)
    
    # make index of integer positions of labels that are not missing
    not_missing = np.array([pos for pos, _ in enumerate(~mask) if _ ])
    
    # transform label data
    labels = scaler.fit_transform(labels)
    
    # stack all features into one array 
    stacked_features = np.stack((feature_dict[var] for var in variables), axis=-1)
    
    # only keep samples that are not missing in the label
    stacked_features = stacked_features[not_missing]
    
    print('features shape: {}'.format(stacked_features.shape))
    print('labels shape: {}'.format(labels.shape))
    
    return stacked_features, labels, index[not_missing]


def daily_train_valid_test_split(X, y, index, ret_test_index=True, test_size=.15, valid_size=.15, random_state=7):
    
    """Split data into train, test and validation set while keeping all hours of one day within one set. Data is only
    splitted in daily chunks."""
    
    assert len(X) == len(y) == len(index), 'Input dimensions not matching'
    
    # transform %-set sizes to appropriate 24 hour chunks
    len_test = int(len(X) // (1 / test_size) // 24)
    len_valid = int(len(X) // (1 / valid_size) // 24)
    
    # get integer representation of available days in the dataset
    available_days = index.map(lambda t: t.date()).unique()
    
    # randomly pick days for test and validation set
    rnd = np.random.RandomState(random_state)
    indices = rnd.choice(available_days, size=len_test+len_valid)
    
    # slice data into subsets by getting all hour-entries for the respective days chosen for that subset
    ix_test = [i for i, date in enumerate(index.date) if date in indices[:len_test]]
    ix_valid = [i for i, date in enumerate(index.date) if date in indices[len_test:]]
    ix_train = [i for i, date in enumerate(index.date) if not date in indices]
    
    X_train = X[ix_train]
    y_train = y[ix_train]
    X_test = X[ix_test]
    y_test = y[ix_test]
    X_valid = X[ix_valid]
    y_valid = y[ix_valid]
    
    if ret_test_index:
        return X_train, X_valid, X_test, y_train, y_valid, y_test, indices[ix_test]
    else:
        return X_train, X_valid, X_test, y_train, y_valid, y_test