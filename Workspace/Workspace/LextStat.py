from pipeline import *
from lingpy.basic.wordlist import * 
from lingpy import LexStat
import sys
def writeToFile():
    print("LOAD TEST WORDLIST")
    pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv"
    
    languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, )
    with codecs.open("lexstat_wordlist.txt","w",encoding="UTF-8") as f:
        f.write("CONCEPT\tIPA\tDOCULECT\tCOGID\n")
        for l,w,gi,cog in zip(languages,words,global_ids,cognate_classes):
            f.write(str(gi)+"\t"+w+"\t"+l+"\t"+cog+"\n")
    wl =get_wordlist("lexstat_wordlist.txt",delimiter="\t")
    print(wl.get_dict(concept="730",entry="IPA"))
    print("initializing lexstat")
    lex = LexStat(wl)
    print("getting scorer")
    lex.get_scorer()
    print("clustering")
    lex.cluster(method="lexstat", threshold=0.6, ref="cognate_class_pred")
    print("output")
    lex.output('tsv', filename="lexstat_ielex")
    
    from lingpy.evaluate.acd import bcubes, diff
    bcubes(lex, "cognate_class", "COGID")
    print(bcubes(lex, "cognate_class", "cognate_class_pred"))
    
def printMeasures():
    y_true = []
    y_pred  =[]
    print("reading")
    for line in codecs.open("lexstat_ielex.tsv","r",encoding="utf-8"):
        line = line.split("\t")
        if len(line)> 2:
            y_true.append(line[4])
            y_pred.append(line[-1])
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    print("calculating")
    ars = metrics.adjusted_rand_score(y_true, y_pred)
    ami = metrics.adjusted_mutual_info_score(y_true, y_pred)
    h,c,v = metrics.homogeneity_completeness_v_measure(y_true, y_pred)
    print(ars,ami,h,c,v)
#writeToFile()
printMeasures()