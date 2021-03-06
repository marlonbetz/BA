import numpy as np 
import regex  
import codecs
import sys
from scipy.spatial.distance import cosine
from sklearn.neighbors import KNeighborsClassifier
import phoneme_embeddings_evaluation
from pipeline import *
from phoneme_embeddings import *
import pickle
from pandas import DataFrame
def vectorLinspace(start,stop,num=50):
    assert len(start) == len(stop)
    assert num > 0
    return np.array([np.linspace(start[dim],stop[dim],num) for dim in range(len(start))]).transpose()

def getListofASJPPhonemes(word):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    return regex.findall(phonemeSearchRegex, word)



def getPerformance(pathToAnnotatedWordList,topn):

#     """
#     COUNT PHONEMES
#     """
#     print("COUNT PHONEMES")
#     freq_phonemes = dict()
#     for i,word in enumerate(allWords):
#         for phoneme in word:
#             if phoneme not in freq_phonemes:
#                 freq_phonemes[phoneme] = 0
#             freq_phonemes[phoneme] += 1
#     """
#     REDUCE COMPLEX PHONEMES TO SINGLE PHONEMES IF FREQ SMALLER THAN X
#     """
#     
    
    
    
    
    n_ensemble  =10
    sg = 0
    hs = 1
    dim_embedding = 20
    window =1
    negative = 0
    mean_acc_all = []
    
    tags = set()
    for test in phoneme_embeddings_evaluation.SimilarityTestData:
        for tag in test["tags"]:
            tags.add(tag)
#   vowel_tags = {"apply_nasalized","remove_nasalized","rounded","height"}
    stoplist_tags = {"labialized","palatalized","aspirated","glottalized","complex","apply_nasalized","remove_nasalized"}
    tags = tags - stoplist_tags
    tags = list(tags)
    mean_acc = dict()
    for tag in tags:
        mean_acc[tag] = []
    for c_tmp in range(n_ensemble):
        print("c_tmp",c_tmp)
    
        print("fitting model")
        pe = PhonemeEmbeddings(pathToASJPCorpusFile=pathToAnnotatedWordList,
                               ignoreCoarticulations = True, 
                               sg = sg,
                               size=dim_embedding,
                               window=window, 
                               negative=negative, 
                               hs=hs, min_count=1)
        print("number of phoneme types:",len(pe.w2v_model.vocab.keys()))

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
    
        
        
        
        for i,test in enumerate(phoneme_embeddings_evaluation.SimilarityTestData):
            #check that test is only proceeded if all tags allow for it
            valid = True
            for t in test["tags"]:
                if t not in tags:
                    valid = False
                    break
            if not valid:
                continue
    
            predicted = [s for (s,dist) in pe.w2v_model.most_similar(positive=test["positive"], negative=test["negative"],topn=topn)]
            true = test["true"][0]
            if true in predicted:
                c_true_all+=1
            for tag in tags:
                if tag in test["tags"]:
                    c[tag] += 1
                    if true in predicted:
                        c_true[tag] += 1
        
            
            dist = cosine(pe.w2v_model[predicted[0]],pe.w2v_model[true])
            
            print("positive",test["positive"],
                  "negative",test["negative"],
                  "true",test["true"],
                  "predicted",pe.w2v_model.most_similar(positive=test["positive"], negative=test["negative"],topn=1),
                  "distance to true label",dist)
            
            
        acc_all = c_true_all/len(phoneme_embeddings_evaluation.SimilarityTestData)
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
    #pickle.dump(df,open(fname,"wb"))
    return df

#picklePerformance("data/dataset.tab", fname="mean_acc_pooled_consonants.pkl",topn=1)      
#df = pickle.load(open("mean_acc_pooled_consonants.pkl","rb"))
df = getPerformance("Data/ASJP/dataset.tab", topn=1)

df = df.rename(columns={"cons":"consonant"})
df = df.rename(columns={"apply_nasal":"apply [+nasal]"})
df = df.rename(columns={"apply_voice":"apply [+voice]"})
df = df.rename(columns={"remove_voice":"remove [+voice]"})
df = df.rename(columns={"rounded":"transfer [rounded]"})
df = df.rename(columns={"height":"transfer [high]"})
#df = df.rename(columns={"remove_nasalized":"[-nasalized]"})
#df = df.rename(columns={"apply_nasalized":"[+nasalized]"})

print(df)

x1 = ["consonant","plosive","fricative"]
x2 = ["apply [+nasal]","apply [+voice]","remove [+voice]"] 
x3 = ["vowel","transfer [rounded]","transfer [high]"]#,"[+nasalized]","[-nasalized]"]
import matplotlib.pyplot as plt
import seaborn
plt.subplot(1,3,1)
seaborn.barplot(data=df,order=sorted(x1,key=lambda x: df[x].mean()),color="red")
plt.subplot(1,3,2)
seaborn.barplot(data=df,order=sorted(x2,key=lambda x: df[x].mean()),color="red")
plt.subplot(1,3,3)
seaborn.barplot(data=df,order=sorted(x3,key=lambda x: df[x].mean()),color="red")
plt.show()
