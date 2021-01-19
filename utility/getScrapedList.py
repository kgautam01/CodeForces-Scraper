# Python script for generating a pkl file for already scraped problems from Codeforces. This pickle is consumed by the scraper to avoid scraping these problems again.

import os
import pickle
import sys 
count = 0
l = []
path = sys.argv[1]
for item in os.listdir(path):
    if os.path.isdir(os.path.join(path, item)):
        l.append(item)
        count+=1
print(count)

with open('alreadyExisting.pkl', 'wb') as f:
    pickle.dump(l, f)
