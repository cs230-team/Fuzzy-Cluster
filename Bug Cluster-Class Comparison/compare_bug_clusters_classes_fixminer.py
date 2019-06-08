import pandas as pd
import json
import pickle
import gzip
import numpy as np

with open('defects4j-bugs.json','r',encoding='utf8') as read_file:
        d4_bugs = json.load(read_file)

def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object

clusters = load_zipped_pickle('defects4jcluster.pickle')

bug_patterns = {}

for bug in d4_bugs:
        bug_patterns[bug['program'] + '-' + str(bug['bugId'])] = bug['repairPatterns']

categories = ['tokens','shapes','actions']
categories_dict = {}

for category in categories:
        category_dict = {}
        subset = clusters[clusters['type'] == category]
        subset = subset.reset_index()
        for i in range(len(subset)):
                idx = subset.loc[i]['cid'][0].rfind('-')
                cluster_num = int(subset.loc[i]['cid'][0][idx+1:])
                for bug in subset.loc[i]['defects4j']:
                        if cluster_num in category_dict:
                                for pattern in bug_patterns[bug]:
                                        if pattern in category_dict[cluster_num]:
                                                category_dict[cluster_num][pattern] += 1
                                        else:
                                                category_dict[cluster_num][pattern] = 1
                                category_dict[cluster_num]['bug_count'] += 1
                        else:
                                category_dict[cluster_num] = {}
                                for pattern in bug_patterns[bug]:
                                        category_dict[cluster_num][pattern] = 1
                                category_dict[cluster_num]['bug_count'] = 1
        categories_dict[category] = category_dict