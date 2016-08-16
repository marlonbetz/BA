import regex
import numpy as np

def ngrams(input, n):
    output = []
    for i in range(len(input)-n+1):
        output.append(input[i:i+n])
    return output
def skippedNgrams(input,n):
    return [ngram[0]+ngram[-1] for ngram in ngrams(input, n)]
def dice(s1,s2):
    return (2*len(set(ngrams(s1,2)).intersection(ngrams(s2,2))) )/ (len(ngrams(s1,2))+len(ngrams(s2,2)))

def xdice(s1,s2):
    return (2*len(set(skippedNgrams(s1,3)).intersection(skippedNgrams(s2,3))) )/ (len(skippedNgrams(s1,3))+len(skippedNgrams(s2,3)))


def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

def normalized_levenshtein(a,b):
    
    return levenshtein(a, b) / np.max([len(a),len(b)])