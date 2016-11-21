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
center_index = np.where(idx_sorted == 0)[0][0]
non_rank_value = pr[idx_sorted[center_index]]
total_count = len(pr)
positive_count = 0
negative_count = 0
for i in xrange(center_index, 0, -1):
  if pr[idx_sorted[i]] > non_rank_value:
    positive_count = i + 1
    break
for i in xrange(center_index, total_count):
  if pr[idx_sorted[i]] < non_rank_value:
    negative_count = total_count - i
    break

print "Total count: %d" % total_count
print "Positive count: %d" % positive_count
print "Neutral count: %d" % (total_count - positive_count - negative_count)
print "Negative count: %d" % negative_count

print "\ntop"
for i in idx_sorted[:10]:
  print ids[i], "=", pr[i]

print "\ncenter ", center_index
for i in idx_sorted[center_index-5:center_index+5]:
  print ids[i], "=", pr[i]

print "\nbottom"
for i in idx_sorted[-10:]:
  print ids[i], "=", pr[i]
