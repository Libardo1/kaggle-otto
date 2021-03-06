"""
This is the global file.
Everything in here should be functions and callable.
"""

from __future__ import print_function, division, with_statement

import numpy as np
import scipy as sp
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss

import sys
import cPickle as pickle
import itertools
import gc


def float32(k):
    return np.cast['float32'](k)

def int32(k):
    return np.cast['int32'](k)


def log_loss_mc(y_true, y_pred, eps=1e-15, normalize=True, sample_weight=None):
    """ Multiclass logloss
    Exactly http://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html#sklearn.metrics.log_loss .
    See https://www.kaggle.com/c/otto-group-product-classification-challenge/details/evaluation .
    """
    ll = log_loss(y_true, y_pred, eps, normalize, sample_weight)
    return ll


def turn_class_list_to_int_list(my_array):
    """
    Becasue xgboost uses [0, classes_num) .
    """
    my_map = {
        'Class_1': 0, 
        'Class_2': 1, 
        'Class_3': 2, 
        'Class_4': 3, 
        'Class_5': 4, 
        'Class_6': 5,
        'Class_7': 6, 
        'Class_8': 7, 
        'Class_9': 8
    }
    new_array = np.copy(my_array)
    for k, v in my_map.iteritems():
        new_array[my_array==k] = v
    return new_array.astype('int')


def load_train_data(path=None, train_size=0.8, full_train=False, scale_it=False, square_root_it=False, square_root_base=0.375):
    """
    Load the train data.
    If full_train=False (default), the function would return (X_train, X_valid, y_train, y_valid, scaler) based on the train_size.
    If full_train=True, the function would also return (X_train, X_valid, y_train, y_valid, scaler), but where in fact X_valid and y_valid are None.
    """
    if path is None:
        try:
            # Unix
            df = pd.read_csv('data/train.csv')
        except IOError:
            # Windows
            df = pd.read_csv('data\\train.csv')
    else:
        df = pd.read_csv(path)
    X = df.values.copy()
    np.random.shuffle(X)
    X[:, -1] = turn_class_list_to_int_list(X[:, -1])
    X = X.astype(float)

    # square root it?
    if square_root_it:
        X[:, 1:-1] = np.sqrt(X[:, 1:-1] + square_root_base)

    # whether scale it or not, we return the scaler!
    scaler = StandardScaler()
    scaler = scaler.fit(X[:, 1:-1])
    if scale_it:
        X[:, 1:-1] = scaler.transform(X[:, 1:-1])

    if not full_train:
        X_train, X_valid, y_train, y_valid = train_test_split(
        X[:, 1:-1], X[:, -1], train_size=train_size,
    )
        print('Loaded training data and splited it into training and validating.')
        return (X_train.astype(float), X_valid.astype(float),
            y_train.astype(int), y_valid.astype(int), scaler)

    elif full_train:
        X_train, X_valid, y_train, y_valid = X[:, 1:-1], None, X[:, -1], None
        print('Loaded training data.')
        return (X_train.astype(float), X_valid,
            y_train.astype(int), y_valid, scaler)


def load_test_data(path=None, scaler=None, square_root_it=False, square_root_base=0.375):
    """
    Load the test data.
    It returns (X_test, X_test_ids).
    """
    if path is None:
        try:
            # Unix
            df = pd.read_csv('data/test.csv')
        except IOError:
            # Windows
            df = pd.read_csv('data\\test.csv')
    else:
        df = pd.read_csv(path)
    X = df.values
    X = X.astype(float)
    
    X_test, X_test_ids = X[:, 1:].astype(float), X[:, 0].astype(int)

    if square_root_it:
        X_test = np.sqrt(X_test + square_root_base)

    # we want to scale it based on the training set!
    if not (scaler is None):
        X_test = scaler.transform(X_test)

    print('Loaded testing data.')
    return X_test, X_test_ids


def df_to_csv(df, path_or_buf='hey-submission.csv', index=False, *args, **kwargs):
    """
    Save pd.DataFrame to csv, defaultly to 'hey-submission.csv'.
    """
    df.to_csv(path_or_buf, index=index, *args, **kwargs)
    tmp = pd.read_csv(path_or_buf)
    print(tmp.head())
    return True


def draft_grid_run(param_grid, fun):
    """
    param_grid is a pd.DataFrame.
    So we run fun(**param_grid_row) again and again,
    and store the result inside results (a list) every time.
    """
    results = []
    for row_index, param_grid_row in param_grid.iterrows():
        gc.collect()
        param_grid_row = param_grid_row.to_dict()
        for k,v in param_grid_row.iteritems():
            # convert back to native python type
            param_grid_row[k] = v.item()
        sys.stderr.write('running {}-th, w/ parameters {}\n'.format(row_index, param_grid_row))
        result = fun(**param_grid_row)
        results.append(result)
        gc.collect()
    return results


def expand_grid(*args, **kwargs):
    """
    http://stackoverflow.com/questions/12130883/r-expand-grid-function-in-python

    expand_grid([0,1], [1,2,3])
    expand_grid(a=[0,1], b=[1,2,3])
    expand_grid([0,1], b=[1,2,3])
    """
    columns = []
    lst = []
    if args:
        columns += xrange(len(args))
        lst += args
    if kwargs:
        columns += kwargs.iterkeys()
        lst += kwargs.itervalues()
    return pd.DataFrame(list(itertools.product(*lst)), columns=columns)

def cbind_lists(*args, **kwargs):
    df = pd.DataFrame()
    if args:
        for arg in args:
            df = pd.concat([df, pd.DataFrame(arg)], axis = 1)
    if kwargs:
        for kwarg in kwargs:
            print(kwarg)
            df = pd.concat([df, pd.DataFrame(kwarg)], axis = 1)

    return df

def save_variable(obj, file_name, recursionlimit=10000):
    sys.setrecursionlimit(recursionlimit)
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, -1)
    return True

def load_variable(file_name):
    """
    usage: something = load_variable('hey.pickle')
    """
    return pickle.load(open(file_name, 'rb'))


def average_of_list_of_dfs(list_of_dfs):
    """
    given a list of dfs, return the average of those dfs
    """
    k = pd.concat(list_of_dfs)
    av = k.groupby(k.index).mean()
    return av


def proba_mat_to_df(proba_mat):
    nrow_test = proba_mat.shape[0]
    X_test_ids = np.array(range(1, nrow_test+1))
    df = pd.concat([pd.Series(X_test_ids), pd.DataFrame(proba_mat)], axis=1)
    df.columns = ['id','Class_1','Class_2','Class_3', 'Class_4', 'Class_5', 'Class_6', 'Class_7', 'Class_8', 'Class_9']
    return df
