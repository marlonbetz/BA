import matplotlib.pyplot as plt
from pandas import DataFrame
import codecs
import pickle
import numpy as np
from sklearn.manifold import TSNE
pathToWorkspace = "/home/marlon/Documents/BA-master/"
pathToWorkspace = "/Users/marlon/Documents/BA/"

asjp_words = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono/asjp_words.pkl","rb"))
concepts_oneHots = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono/concepts_oneHots.pkl","rb"))
concepts = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono/concepts.pkl","rb"))
embeddings = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono/embeddings.pkl","rb"))
langs = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono/langs.pkl","rb"))
cognate_classes = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono/cognate_classes.pkl","rb"))
print(embeddings[0])
print(embeddings[1])
if embeddings.shape[1] != 2:
    print("tsne")
    tsne = TSNE(2)
    embeddings_transformed = tsne.fit_transform(embeddings)
else:
    embeddings_transformed = embeddings

print("plotting")
import matplotlib.pyplot as plt
import seaborn
cmap = dict((key,np.random.beta(1,1,3)) for key in cognate_classes)
n = len(embeddings_transformed)
plt.scatter(embeddings_transformed[:n,0],embeddings_transformed[:n,1],alpha=0.1)
#seaborn.kdeplot(embeddings_transformed[:10000,0],embeddings_transformed[:10000,1])
        

plt.show()