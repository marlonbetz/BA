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

allWords = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_geo_binary_asjp/allWords.pkl","rb"))
embeddings = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_geo_binary_asjp/embeddings.pkl","rb"))
concepts = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_geo_binary_asjp/concepts.pkl","rb"))
languages = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_geo_binary_asjp/languages.pkl","rb"))

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
langs = set(languages)
cmap = sns.color_palette("hls", len(langs))
language_id = dict((lang,i) for i,lang in enumerate(langs))

n = len(embeddings_transformed)
bins = dict()
for i,language in enumerate(languages[:n]):
    if language not in bins:
        bins[language] = []
    bins[language].append(i)
alpha = 0.01
for language in bins:
    plt.scatter(embeddings_transformed[bins[language],0],embeddings_transformed[bins[language],1],color=cmap[language_id[language]],alpha=alpha,label=str(language))
#plt.legend(title="word length",frameon=True)
#for word, emb in zip(allWords[:n],embeddings_transformed):
#    l = np.min([15,len(getListofASJPPhonemes(word))])
#    plt.scatter(emb[0],emb[1],alpha=0.1,color=cmap[l-1])   
#plt.scatter(embeddings_transformed[:n,0],embeddings_transformed[:n,1],alpha=0.1)
#seaborn.kdeplot(embeddings_transformed[:n,0],embeddings_transformed[:n,1])
        

plt.show()