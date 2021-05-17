# -*- coding: utf-8 -*-
"""sim_ann_test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pdrTcaTZPs-m38Li-FN6Omp8aHVymcX3
"""

import sys
import numpy as np
from numpy import asarray
from numpy import unique
import xml.dom.minidom
import time
import itertools
from itertools import combinations
from itertools import product
import random
import math
import xml.etree.ElementTree as ET
import scipy
from scipy.constants import k
from scipy import special


def find_max_size(t, no_opts, no_vals):  # Upper bound of the size
    top = np.log(bino_coef(no_opts, t)) + (t * np.log(no_vals))
    bottom = np.log((no_vals**t) / (no_vals**t - 1))
    return int(top / bottom) + 1


def bino_coef(n, k):  # Binomial coefficient function
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0


def create_array(mydict):
    arr = []
    # Takes the cartesian product of options with values. This will create a configuration settings list.
    for i in my_product(mydict):
        arr.append(list(i.values()))
    return asarray(arr)  # This will return the arr with the numpy array form.


def my_product(mydict):
    return (dict(zip(mydict, x)) for x in product(*mydict.values()))


def create_test_array(array, size):
    x = sorted(random.sample(range(array.shape[0]), min(size, array.shape[0])))
    return array[x, :]


def count_miss(data, t, no_vals):
 # print(np.arange(data.shape[1]))
    missing_tuples = 0
    # combinations(): itertools module, creates an array of all the given t combinations of the values
    for p in combinations(np.arange(data.shape[1]), t):
        # check if every possible interaction is represented
        if (np.unique(data[:, p], axis=0).shape[0] < no_vals**t):
            # if not, return false
            missing_tuples = no_vals**t - \
                np.unique(data[:, p], axis=0).shape[0]
            return missing_tuples
    # if we made it through the whole for loop, return true
    return missing_tuples


def check_interactions(data, t, no_vals):
 # print(np.arange(data.shape[1]))
    # combinations(): itertools module, creates an array of all the given t combinations of the values
    for p in combinations(np.arange(data.shape[1]), t):
        # check if every possible interaction is represented
        if (unique(data[:, p], axis=0).shape[0] < no_vals**t):
            # if not, return false
            return False
    # if we made it through the whole for loop, return true
    return True


def cooling_rate(starting_temp, stopping_temp, t, no_opts):
    top = (starting_temp - stopping_temp)
    bottom = 0.15 * ((10**t) * no_opts * t)

    return (top/bottom)


def size_decrease(data):  # Randomly deletes a row in generated array to decrease its size
    dec_data = np.delete(data, random.randint(0, data.shape[0]), 0)
    return dec_data


# Neighboring state generation function which gets the data and alters an option setting value
def neighboring_state_gen(data, no_opts, no_vals, c_size):

    if data.shape[0] == c_size:
        neighbor = data
        c_row = random.randint(0, data.shape[0]-1)
        c_col = random.randint(0, no_opts-1)
        neighbor[c_row, c_col] = random.randint(0, no_vals-1)
    else:
        neighbor = create_test_array(data, c_size)
    return neighbor


doc = xml.dom.minidom.parse(input('Please enter the name of the XML file: '))
mydict = {}
for node in doc.getElementsByTagName('Parameter'):
    if node.hasChildNodes():
        id = node.getAttribute('id')
        values = node.getElementsByTagName('value')
        x = []
        for value in values:
            x += value.firstChild.nodeValue
        mydict[id] = x
    else:
        txt = node.getAttribute('text')
        print(txt)
print(mydict)
arr = create_array((mydict))
print(arr)
t = int(input('Coverage strength(t): '))
# no_opts = int(input('Number of options: '))
# no_vals = int(input('Number of option values for every option: '))
count = 0
value_count = 1
for x in mydict:
    for i in range(0, len(x)):
        value_count *= x[i]
print(count)
print(len(mydict))
no_opts = len(mydict)

starting_temp = 1
stopping_temp = 0.000001
running = 100

#arr = create_array(no_opts, no_vals)
c_size = arr.shape[0]
working_test = create_test_array(arr, c_size)
# test = create_test_array(arr, c_size)
# miss = count_miss(test, t, no_vals)
# if (miss == 0):
#     best = test
# first_array = best
while (running > 0):
    test = create_test_array(arr, c_size)
    # check if all interactions are represented in this test array
    if (check_interactions(test, t, no_vals)):
        # if they are, reduce the covariance size and try again
        c_size = c_size - 1
        working_test = test
    else:
        # else, the iterations if we have a working test
        if (working_test.shape[0] != 0):
            running = running - 1
first_array = best = working_test
print("First array:\n", working_test)
print("Covering array size: ", working_test.shape[0], working_test.shape[1],
      " with the total of ", working_test.shape[0] * working_test.shape[1], " indices.")
print(". . .")
c_rate = cooling_rate(starting_temp, stopping_temp, t, no_opts)
temp = starting_temp
# working_test = create_test_array(test, c_size)
start = time.time()
while temp > stopping_temp:
    working_test = create_test_array(working_test, c_size)
    miss = count_miss(working_test, t, no_vals)
    if (miss == 0):
        best = working_test
        c_size -= 1
        temp = starting_temp
        continue
    neighbor = neighboring_state_gen(working_test, no_opts, no_vals, c_size)
    t_miss_n = count_miss(neighbor, t, no_vals)
    diff_miss = t_miss_n - miss
    if working_test.shape[0] == neighbor.shape[0] or (diff_miss < 0 or (random.randint(0, 1) < (math.e)**((-(scipy.constants.k))*diff_miss/temp))):
        working_test = neighbor
        if count_miss(working_test, t, no_vals) == 0:
            best = working_test
            c_size -= 1
            temp = starting_temp
            continue
    temp = temp - (temp * c_rate)
stop = time.time()
print(stop-start)
c_array = np.unique(best, axis=0)
if c_array.size < first_array.size:
    print("Final missing tuple count: ", count_miss(best, t, no_vals))
    print(c_array)
    print("Covering array size: ", c_array.shape[0], c_array.shape[1],
          " with the total of ", c_array.shape[0] * c_array.shape[1], " indices.")
else:
    print(first_array)
    print("Final missing tuple count: ", count_miss(first_array, t, no_vals))
    print("Covering array size: ", first_array.shape[0], first_array.shape[1],
          " with the total of ", first_array.shape[0] * first_array.shape[1], " indices.")
