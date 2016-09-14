import numpy as np 
import regex  
import codecs
import sys
from scipy.spatial.distance import cosine
from sklearn.neighbors import KNeighborsClassifier
import evaluation
import pickle
from gensim.models import Word2Vec
from pandas import DataFrame
def vectorLinspace(start,stop,num=50):
    assert len(start) == len(stop)
    assert num > 0
    return np.array([np.linspace(start[dim],stop[dim],num) for dim in range(len(start))]).transpose()

def getListofASJPPhonemes(word):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    return regex.findall(phonemeSearchRegex, word)



def picklePerformance(pathToASJPCorpusFile,fname,topn):
    """
    READ CORPUS FROM ASJP DUMP
    """
    print("READ CORPUS FROM ASJP DUMP")
    #pathToASJPCorpusFile = "data/dataset.tab"
    allWords = []
    for i,line in enumerate(codecs.open(pathToASJPCorpusFile,"r","utf-8")):
        if i > 0:
            line = line.split("\t")
            if "PROTO" not in line[0] and "ARTIFICIAL" not in line[2]:
                words = line[10:]
                #remove invalid characters
                for word in words:
                    word = word.replace("%","")
                """
                for cells with more than one corresponding word, add that word as new entry
                """
                tba = []
                for i_w,word in enumerate(words):
                    if "," in word:
                        for match in  regex.findall("(?<=,).+",word):          
                            tba.append(match)
                        #reduce entry to first occurence of seperator
                        words[i_w] = word[:word.index(",")]
                words.extend(tba)
                allWords.extend(words)
       
    """
    EXTRACT ALL PHONEMES AND ADD WORD BOUNDARIES AND GET RID OF EMPTY STRINGS
    """
    print("EXTRACT ALL PHONEMES AND ADD WORD BOUNDARIES AND GET RID OF EMPTY STRINGS")
    allWords = [["<s>"]+getListofASJPPhonemes(word)+["</s>"] for word in allWords if len(word) > 0]
    
    """
    pool complex with plain consonants
    """
    print("pool complex with plain consonants".upper())
    plain_consonants=set("pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!".split())
    for i_w,word in enumerate(allWords):
        tmp = []
        for phoneme in word:
            if phoneme[0] in plain_consonants:
                tmp.append(phoneme[0])
            else:
                tmp.append(phoneme)
        allWords[i_w] = tmp
    """
    COUNT PHONEMES
    """
    print("COUNT PHONEMES")
    freq_phonemes = dict()
    for i,word in enumerate(allWords):
        for phoneme in word:
            if phoneme not in freq_phonemes:
                freq_phonemes[phoneme] = 0
            freq_phonemes[phoneme] += 1
    """
    REDUCE COMPLEX PHONEMES TO SINGLE PHONEMES IF FREQ SMALLER THAN X
    """
    
    
    
    
    
    n_ensemble  =10
    sg = 0
    hs = 1
    dim_embedding = 100
    window = 2
    mean_acc_all = []
    
    tags = set()
    for test in evaluation.SimilarityTestData:
        for tag in test["tags"]:
            tags.add(tag)
    vowel_tags = {"apply_nasalized","remove_nasalized","rounded","height"}
    stoplist_tags = {"labialized","palatalized","aspirated","glottalized","complex"}
    tags = tags - stoplist_tags
    tags = list(tags)
    mean_acc = dict()
    for tag in tags:
        mean_acc[tag] = []
    for c_tmp in range(n_ensemble):
        print("c_tmp",c_tmp)
    
        print("fitting model")
        w2v_model = Word2Vec(sentences=allWords,
                             sg = sg,
                             size=dim_embedding,
                             window=window,
                             hs=hs,
                             min_count=1
                             )
        """
        EVALUATION
        """
        print("EVALUATION")
        c = dict()
        c_true = dict()
        c_true_all = 0
        for tag in tags:
            c[tag] = 0
            c_true[tag] = 0
    
        
        
        
        for i,test in enumerate(evaluation.SimilarityTestData):
            #check that test is only proceeded if all tags allow for it
            valid = True
            for t in test["tags"]:
                if t not in tags:
                    valid = False
                    break
            if not valid:
                continue
    
            predicted = [s for (s,dist) in w2v_model.most_similar(positive=test["positive"], negative=test["negative"],topn=topn)]
            true = test["true"][0]
            if true in predicted:
                c_true_all+=1
            for tag in tags:
                if tag in test["tags"]:
                    c[tag] += 1
                    if true in predicted:
                        c_true[tag] += 1
        
            
            dist = cosine(w2v_model[predicted[0]],w2v_model[true])
            
            print("positive",test["positive"],
                  "negative",test["negative"],
                  "true",test["true"],
                  "predicted",w2v_model.most_similar(positive=test["positive"], negative=test["negative"],topn=1),
                  "distance to true label",dist)
            
            
        acc_all = c_true_all/len(evaluation.SimilarityTestData)
        acc = dict()
        for tag in tags:
            acc[tag] = c_true[tag] / c[tag]
    
    
        print("acc",acc)
        print("acc_all",acc_all)
        mean_acc_all.append(acc_all)
    
        for tag in tags:
            mean_acc[tag].append(acc[tag])
    
    print("mean_acc_all",np.mean(mean_acc_all))
    for tag in tags:
        print(tag,np.mean(mean_acc[tag]))
    df = DataFrame(mean_acc,columns=tags)
    pickle.dump(df,open(fname,"wb"))

#picklePerformance("data/dataset.tab", fname="mean_acc_pooled_consonants.pkl",topn=1)      
df = pickle.load(open("mean_acc_pooled_consonants.pkl","rb"))
df = df.rename(columns={"cons":"consonant"})
df = df.rename(columns={"apply_nasal":"apply [+nasal]"})
df = df.rename(columns={"apply_voice":"apply [+voice]"})
df = df.rename(columns={"remove_voice":"remove [+voice]"})
df = df.rename(columns={"rounded":"transfer [rounded]"})
df = df.rename(columns={"height":"transfer [high]"})
df = df.rename(columns={"remove_nasalized":"[-nasalized]"})
df = df.rename(columns={"apply_nasalized":"[+nasalized]"})

print(df)

x1 = ["consonant","plosive","fricative"]
x2 = ["apply [+nasal]","apply [+voice]","remove [+voice]"] 
x3 = ["vowel","transfer [rounded]","transfer [high]","[+nasalized]","[-nasalized]"]
import matplotlib.pyplot as plt
import seaborn
plt.subplot(1,3,1)
seaborn.barplot(data=df,order=sorted(x1,key=lambda x: df[x].mean()),color="red")
plt.subplot(1,3,2)
seaborn.barplot(data=df,order=sorted(x2,key=lambda x: df[x].mean()),color="red")
plt.subplot(1,3,3)
seaborn.barplot(data=df,order=sorted(x3,key=lambda x: df[x].mean()),color="red")
plt.show()
