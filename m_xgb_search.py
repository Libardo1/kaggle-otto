from __future__ import print_function, division, with_statement

import numpy as np
import scipy as sp
import pandas as pd
from scipy.stats import randint as sp_randint
from sklearn.metrics import log_loss
import xgboost as xgb

from otto_global import load_train_data, load_test_data, df_to_csv, draft_grid_run, expand_grid
from m_xgb import hey_xgb_model, predict_from_xgb_model



# full_X_train, _, full_y_train, _, _ = load_train_data(full_train=True)
# X_test, X_test_ids = load_test_data()


# @opt.cross_validated(x=full_X_train, y=full_y_train, num_folds=3)
# def seach_xgb(x_train, y_train, x_test, y_test, 
#     eta, gamma, max_depth, min_child_weight, max_delta_step, 
#     colsample_bytree, subsample, num_round):
#     xgb_param = {
#         'eta': eta, # maybe low
#         'gamma': gamma, # maybe less than 1
#         'max_depth': int(max_depth), # absolutely less than 10
#         'min_child_weight': int(min_child_weight),
#         'max_delta_step': max_delta_step,
#         'colsample_bytree': colsample_bytree,
#         'subsample': subsample,
#         'objective': 'multi:softprob',
#         'eval_metric': 'mlogloss',
#         'num_class': 9,
#         'nthread': 8
#     }
#     num_round = int(num_round)

#     bst = hey_xgb_model(x_train, None, y_train, None,
#         xgb_param=xgb_param, num_round=num_round)

#     pred = predict_from_xgb_model(bst, x_test)
#     ll = log_loss(y_test,pred.iloc[:,1:].as_matrix())

#     return ll

# # impossible to compute in a reasonable time
# optimal_pars, details, _ = opt.minimize(seach_xgb, 
#     num_evals=10,
#     eta=[0, 1], 
#     gamma=[0, 1], 
#     max_depth=[0, 10], 
#     min_child_weight=[0.9, 10.1], 
#     max_delta_step=[0, 1], 
#     colsample_bytree=[0, 1], 
#     subsample=[0, 1], 
#     num_round=[100, 10000]
# )


train_size=0.85
X_train, X_valid, y_train, y_valid, _ = load_train_data(train_size=train_size)
X_test, X_test_ids = load_test_data()
def grid_xgb_wrapper(eta=0.3, 
    gamma=1.0, 
    max_depth=10, 
    min_child_weight=4, 
    max_delta_step=0, 
    colsample_bytree=0.8, 
    subsample=0.9, 
    num_round=250,
    num_fold=3,
    nthread=8,
    early_stopping_rounds=100):
    xgb_param = {
        'eta': eta, # maybe low
        'gamma': gamma, # maybe less than 1
        'max_depth': int(max_depth), # absolutely less than 10
        'min_child_weight': int(min_child_weight),
        'max_delta_step': max_delta_step,
        'colsample_bytree': colsample_bytree,
        'subsample': subsample,
        'objective': 'multi:softprob',
        'eval_metric': 'mlogloss',
        'num_class': 9,
        'nthread': nthread,
        'seed': np.random.randint(0, 2**32)
    }
    num_round = int(num_round)
    bst = hey_xgb_model(X_train, X_valid, y_train, y_valid, xgb_param, num_round, num_fold, early_stopping_rounds=early_stopping_rounds, use_cv=False)
    return None

#param_grid = expand_grid(eta=[0.05], num_round=[2000], gamma=[0.9,0.8,0.7], max_depth=[5],min_child_weight=[4,5],colsample_bytree=[0.5, 0.75,0.78,0.8, 0.82,0.85], subsample=[0.5, 0.8,0.88,0.9,0.92], early_stopping_rounds=[99])
param_grid = expand_grid(eta=[0.04], num_round=[4000], gamma=[0.7,0.75,0.85, 0.9], max_depth=[5,6,7],min_child_weight=[4,5, 6],colsample_bytree=[0.5, 0.6, 0.7, 0.75], subsample=[0.5, 0.65, 0.8, 0.88], early_stopping_rounds=[100], nthread=[36])
gird_1 = draft_grid_run(param_grid, grid_xgb_wrapper)
