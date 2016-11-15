import sys
from pageRank import pageRank

import numpy as np

def read_file(filename, filename2):
    ids = [-1]
    idx_map = {}

    with open(filename, 'r') as f:
      for line in f:
          (frm, to) = line.strip().split(" ")
          ids += [frm, to]

    with open(filename2, 'r') as f:
      for line in f:
          (frm, to) = line.strip().split(" ")
          ids += [frm, to]

    ids = np.unique(ids)
    for i, id in enumerate(ids):
      idx_map[id] = i

    links = [[] for _ in xrange(len(ids))]

    with open(filename, 'r') as f:
      for line in f:
          (frm, to) = line.strip().split(" ")
          frm, to = idx_map[frm], idx_map[to]
          links[frm].append(to)

    with open(filename2, 'r') as f:
      for line in f:
          (frm, to) = line.strip().split(" ")
          frm, to = idx_map[frm], idx_map[to]
          if to in links[frm]:
            links[frm].remove(to) 
          links[frm].append(-to)

    return links, ids, idx_map

negative_file = len(sys.argv) > 2 and sys.argv[2] or '/dev/null'
links, ids, idx_map = read_file(sys.argv[1], negative_file)

pr = pageRank(links, alpha=0.85, convergence=0.00001, checkSteps=1)
idx_sorted = np.argsort(pr)[::-1]

print "\ntop"
for i in idx_sorted[:10]:
  print ids[i], "=", pr[i]

center_index = np.where(idx_sorted == 0)[0][0]
print "\ncenter ", center_index
for i in idx_sorted[center_index-5:center_index+5]:
  print ids[i], "=", pr[i]

print "\nbottom"
for i in idx_sorted[-10:]:
  print ids[i], "=", pr[i]
