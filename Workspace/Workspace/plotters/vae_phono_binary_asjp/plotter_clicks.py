import matplotlib.pyplot as plt
from pandas import DataFrame
import codecs
import pickle
import numpy as np
from sklearn.manifold import TSNE
import regex
def getListofASJPPhonemes(word):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    return regex.findall(phonemeSearchRegex, word)


pathToWorkspace = "/home/marlon/Documents/BA-master/"
pathToWorkspace = "/Users/marlon/Documents/BA/"
pathToWorkspace = "/home/marlon/Documents/BA-master/"
pathToWorkspace = "/Users/marlon/Documents/BA/"

allWords = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_binary_asjp/allWords.pkl","rb"))
embeddings = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_binary_asjp/embeddings.pkl","rb"))

if embeddings.shape[1] != 2:
    print("tsne")
    tsne = TSNE(2)
    embeddings_transformed = tsne.fit_transform(embeddings)
else:
    embeddings_transformed = embeddings

print("plotting")

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

from binary_phoneme_features import BinaryPhonemeFeatures

bpf = BinaryPhonemeFeatures()

cmap = sns.color_palette("hls", 2)


n = len(embeddings_transformed)
#n = 4000
bins = dict()
for i,word in enumerate(allWords[:n]):
    contains_feature = False
    for phoneme in getListofASJPPhonemes(word):
        if bpf.hasFeature(phoneme, "click"):
            contains_feature = True
            break
    if contains_feature:
        if "click" not in bins:
            bins["click"] = []
        bins["click"].append(i)
    else:
        if "no click" not in bins:
                bins["no click"] = []
        bins["no click"].append(i)
        
    


plt.scatter(embeddings_transformed[bins["no click"],0],embeddings_transformed[bins["no click"],1],color=cmap[0],alpha=0.1,label="no clicks")
plt.scatter(embeddings_transformed[bins["click"],0],embeddings_transformed[bins["click"],1],color=cmap[1],alpha=0.1,label="clicks")
plt.legend(frameon=True)

#for word, emb in zip(allWords[:n],embeddings_transformed):
#    l = np.min([15,len(getListofASJPPhonemes(word))])
#    plt.scatter(emb[0],emb[1],alpha=0.1,color=cmap[l-1])   
#plt.scatter(embeddings_transformed[:n,0],embeddings_transformed[:n,1],alpha=0.1)
#seaborn.kdeplot(embeddings_transformed[:n,0],embeddings_transformed[:n,1])
        

plt.show()