import datetime as dt
import numpy as np
import pandas as pd
import os
from functools import reduce


def prepare_training_data(months=range(1, 13, 1), inputs=['SWDIFDS_RAD', 'SWDIRS_RAD'], return_index=True, 
                         base_path='./processed_data/weather', scale=True):
    
    indices = {}
    tensors = {}
    
    for variable in inputs:
        
        index_arr = []
        data_arr = []
        amax = 0

        for month in months:
            
            date = dt.date(2015, month, 1).strftime('%Y%m')
            filename = os.path.join(base_path, '{}.2D.{}'.format(variable, date))
            
            index_arr.append(pd.read_csv('{}.txt'.format(filename), parse_dates=True, header=None, index_col=0))
            
            data = np.load('{}.npy'.format(filename))
            
            max_val = np.amax(data)
            
            if scale:
                amax = max(amax, max_val)
            
            data_arr.append(data)
        
        if scale:
            data_arr /= amax

        indices[variable] = pd.concat(index_arr).index
        tensors[variable] = np.vstack(data_arr)

    if return_index:
        return indices, tensors
    else:
        return tensors
    

def check_indices(indices):
    
    missing = dict([(key, None) for key in indices.keys()])
    
    common_index = reduce(lambda  left,right: left.join(right, how='outer'), indices.values())
    
    for key, val in indices.items():
        missing[key] = common_index.difference(val)
        
    return missing


def align_transform_data(labels, feature_dict, variables, scaler, index):
    
    mask = labels.isnull().values
    labels.dropna(inplace=True)
    
    not_missing = np.array([pos for pos, _ in enumerate(~mask) if _ ])
    labels = scaler.fit_transform(labels)
    
    stacked_features = np.stack((feature_dict[var] for var in variables), axis=-1)
    stacked_features = stacked_features[not_missing]
    
    print('features shape: {}'.format(stacked_features.shape))
    print('labels shape: {}'.format(labels.shape))
    
    return stacked_features, labels, index[not_missing]


def daily_train_valid_test_split(X, y, index, ret_test_index=True, test_size=.15, valid_size=.15, random_state=7):
    
    assert len(X) == len(y) == len(index), 'Input dimensions not matching'
    
    len_test = int(len(X) // (1 / test_size) // 24)
    len_valid = int(len(X) // (1 / valid_size) // 24)
        
    available_days = index.map(lambda t: t.date()).unique()
    
    rnd = np.random.RandomState(random_state)
    indices = rnd.choice(available_days, size=len_test+len_valid)
        
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