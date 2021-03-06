import matplotlib.pyplot as plt
from pandas import DataFrame
import codecs
import pickle
import numpy as np
from sklearn.manifold import TSNE
pathToWorkspace = "/home/marlon/Documents/BA-master/"
asjp_words = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/asjp_words.pkl","rb"))
concepts_oneHots = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/concepts_oneHots.pkl","rb"))
concepts = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/concepts.pkl","rb"))
embeddings_concept = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/embeddings_concept.pkl","rb"))
embeddings_geo = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/embeddings_geo.pkl","rb"))
embeddings = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/embeddings.pkl","rb"))
geo_words_scaled = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/geo_words_scaled.pkl","rb"))
langs = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/langs.pkl","rb"))
cognate_classes = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/local_manifold_learning/cognate_classes.pkl","rb"))

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
for asjp_word,emb,cognate_class,concept in zip(asjp_words,embeddings_transformed,cognate_classes,concepts):
    if concept == 0:
        plt.subplot(2,2,1)
        plt.annotate(asjp_word,emb,color=cmap[cognate_class])
    if concept == 1:
        plt.subplot(2,2,2)
        plt.annotate(asjp_word,emb,color=cmap[cognate_class])
    if concept == 2:
        plt.subplot(2,2,3)
        plt.annotate(asjp_word,emb,color=cmap[cognate_class])
    if concept == 3:
        plt.subplot(2,2,4)
        plt.annotate(asjp_word,emb,color=cmap[cognate_class])

plt.show()