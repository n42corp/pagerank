# PageRank Python implementation by Vincent Kraeutler, at:
# http://kraeutler.net/vincent/essays/google%20page%20rank%20in%20python
#
# The code has the following changes from the original:
#
# * The data types were converted from 32 bits to 64 bits and precision
#
# * The convergence criterion was changed from the average deviation
# to the Euclidean 1-norm distance, which is tighter
# 
# The original code was released by Vincent Kraeutler under a Creative
# Commons Attribution 2.5 License
#

#!/usr/bin/env python

from numpy import *

def normalize(x):
    m = min(x)
    if m >= 0:
      return x
    x -= m
    m = max(x)
    if m > 1:
      x /= m
    return x / sum(x)

def pageRankGenerator(At = [array((), int64)], 
                      numLinks = array((), int64),  
                      ln = array((), int64),
                      negNumLinks = array((), int64),
                      negLn = array((), int64),
                      alpha = 0.85, 
                      convergence = 0.0001, 
                      checkSteps = 10,
                      negativeRatio = 2.0
                      ):
    """
    Compute an approximate page rank vector of N pages to within
    some convergence factor.

    @param At a sparse square matrix with N rows. At[ii] contains
    the indices of pages jj linking to ii.

    @param numLinks iNumLinks[ii] is the number of links going out
    from ii.

    @param ln contains the indices of pages without links

    @param alpha a value between 0 and 1. Determines the relative
    importance of "stochastic" links.

    @param convergence a relative convergence criterion. Smaller
    means better, but more expensive.

    @param checkSteps check for convergence after so many steps
    """

    # the number of "pages"
    N = len(At)

    # the number of "pages without links"
    M = ln.shape[0]

    # initialize: single-precision should be good enough
    iNew = ones((N,), float64) / N
    iOld = ones((N,), float64) / N

    checks_count = 0
    done = False
    pre_diff = 10000000
    negNumRatio = 1.0 * negNumLinks.take(negLn, axis = 0) / numLinks.take(negLn, axis = 0)

    while not done:
        checks_count += 1

        # normalize every now and then for numerical stability
        iNew /= sum(iNew)

        for step in range(checkSteps):

            # swap arrays
            iOld, iNew = iNew, iOld

            # an element in the 1 x I vector. 
            # all elements are identical.
            oneIv = (1 - alpha) * sum(iOld) / N

            # an element of the A x I vector.
            # all elements are identical.
            oneAv = 0.0
            if M > 0:
                neg_sum = dot(iOld.take(negLn, axis = 0), negNumRatio) * (negativeRatio + 1)
                oneAv = alpha * (sum(iOld.take(ln, axis = 0)) + neg_sum) / N

            # the elements of the H x I multiplication
            ii = 0 
            while ii < N:
                page = At[ii]
                h = 0
                if page.shape[0]:
                    sign = (page >= 0) * 1 + (page < 0) * -negativeRatio
                    page = abs(page)
                    h = alpha * dot(
                            iOld.take(page, axis = 0) * sign,
                            1. / numLinks.take(page, axis = 0)
                            )
                iNew[ii] = h + oneAv + oneIv
                ii += 1

            iNew = normalize(iNew)

        diff = sum(abs(iNew - iOld))
        print "diff: %20f" % diff
        done = (diff < convergence)
        pre_diff = diff

        if done:
          add = 1 - sum(iNew)
          if add > 0:
            iNew += add / N
          print "sum: %f" % sum(iNew)
          print "checks count: %d" % checks_count

        yield iNew


def transposeLinkMatrix(
        outGoingLinks = [[]]
        ):
    """
    Transpose the link matrix. The link matrix contains the pages
    each page points to. But what we want is to know which pages
    point to a given page, while retaining information about how
    many links each page contains (so store that in a separate
    array), as well as which pages contain no links at all (leaf
    nodes).

    @param outGoingLinks outGoingLinks[ii] contains the indices of
    pages pointed to by page ii

    @return a tuple of (incomingLinks, numOutGoingLinks, leafNodes)
    """

    nPages = len(outGoingLinks)
    # incomingLinks[ii] will contain the indices jj of the pages
    # linking to page ii
    incomingLinks = [[] for ii in xrange(nPages)]
    # the number of links in each page
    numLinks = zeros(nPages, int64)
    # the indices of the leaf nodes
    leafNodes = []
    negNodes = []
    negNumLinks = zeros(nPages, int64)

    for ii in xrange(nPages):
        if len(outGoingLinks[ii]) == 0:
            leafNodes.append(ii)
        else:
            negCount = 0
            numLinks[ii] = len(outGoingLinks[ii])
            # transpose the link matrix
            for jj in outGoingLinks[ii]:
                if jj < 0:
                  negCount += 1
                  incomingLinks[-jj].append(-ii)
                else:
                  incomingLinks[jj].append(ii)
            if negCount > 0:
              negNodes.append(ii)
              negNumLinks[ii] = negCount

    incomingLinks = [array(ii) for ii in incomingLinks]
    numLinks = array(numLinks)
    leafNodes = array(leafNodes)

    return incomingLinks, numLinks, leafNodes, negNumLinks, negNodes


def pageRank(
        linkMatrix = [[]],
        alpha = 0.85, 
        convergence = 0.0001, 
        checkSteps = 10
        ):
    """
    Convenience wrap for the link matrix transpose and the generator.

    @see pageRankGenerator for parameter description
    """
    incomingLinks, numLinks, leafNodes, negNumLinks, negNodes = transposeLinkMatrix(linkMatrix)

    for gr in pageRankGenerator(incomingLinks, numLinks, leafNodes, negNumLinks, negNodes,
                                alpha = alpha, convergence = convergence,
                                checkSteps = checkSteps):
        final = gr

    return final

