#!/usr/bin/python
"""
Adapted from:

http://martinos.org/mne/stable/auto_examples/decoding/plot_decoding_sensors.html#example-decoding-plot-decoding-sensors-py

"""

import matplotlib
matplotlib.use('cairo')
import matplotlib.pyplot as plt

import pylab as pl


import numpy as np
from scipy.io import loadmat

from sklearn.svm import SVC
from sklearn.cross_validation import cross_val_score, ShuffleSplit

import joblib
from joblib import Parallel, delayed

def do_sensor(X, y, i, begin, end ):
    clf = SVC(C=1, kernel='linear')
    
    # Define a monte-carlo cross-validation generator (reduce variance):
    cv = ShuffleSplit(len(X), 10, test_size=0.2)
    
    Xi = X[:, i, begin:end]
    # Standardize features
    Xi -= Xi.mean(axis=0)
    Xi /= Xi.std(axis=0)
    # Run cross-validation
    # Note : for sklearn the Xt matrix should be 2d (n_samples x
    # n_features)
    scores_t = cross_val_score(clf, Xi, y, cv=cv, n_jobs=1)

    return scores_t.mean(),scores_t.std()

time_selection = np.load("numpy_data/mean_time_selection.npy")
time_selection = np.nonzero( time_selection > 0.55 )[0]
print time_selection
begin = time_selection[0]
end = time_selection[-1]+1

print begin,end

all_scores = []
all_std = []
for subject in xrange(1,17):
    filename = 'data/train_subject%02d.mat' % subject
    print "Loading", filename
    data = loadmat(filename, squeeze_me=True)
    X = data['X']
    y = data['y']

    # X = X[:10]
    # y = y[:10]

    n_sensors = X.shape[1]

    mean_std = Parallel(n_jobs=-1)(delayed(do_sensor)(X,y,i,begin,end) for i in range(n_sensors))

    scores = np.array( [s[0] for s in mean_std] )
    std_scores = np.array( [s[1] for s in mean_std] )
    
    all_scores.append(scores)
    all_std.append( std_scores)

scores = np.array(all_scores).mean(axis=0)
#std_scores = np.array(all_std).mean(axis=0)
std_scores = np.array(all_scores).std(axis=0)

np.save("numpy_data/mean_sensor_selection.npy", scores)
np.save("numpy_data/std_sensor_selection.npy", std_scores)

sensors = map( str, range(306) )
x_pos = np.arange(len(sensors))

scores *= 100  # make it percentage
std_scores *= 100

fig = plt.figure( figsize=(40, 8) )

plt.bar(x_pos, scores, yerr=std_scores, alpha=0.4, align='center')

plt.axhline(50, color='r', linestyle='--',
            label="Chance level")

plt.xticks(x_pos, sensors)
plt.xlabel('Sensor')
plt.title('Sensor performance')
plt.savefig('img/sensor_selection.png', bbox_inches='tight' )

