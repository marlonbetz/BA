import matplotlib.pyplot as plt
from pandas import DataFrame
import codecs
import pickle
import numpy as np
from sklearn.manifold import TSNE
pathToWorkspace = "/home/marlon/Documents/BA-master/"
pathToWorkspace = "/Users/marlon/Documents/BA/"

allWords = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_binary_asjp/allWords.pkl","rb"))
embeddings = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_binary_asjp/embeddings.pkl","rb"))
concepts = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_binary_asjp/concepts.pkl","rb"))
languages = pickle.load(codecs.open(pathToWorkspace+"Workspace/Workspace/embeddings/vae_phono_concept_binary_asjp/languages.pkl","rb"))

if embeddings.shape[1] != 2:
    print("tsne")
    tsne = TSNE(2)
    embeddings_transformed = tsne.fit_transform(embeddings)
else:
    embeddings_transformed = embeddings
    #tsne = TSNE(2)
    #embeddings_transformed = tsne.fit_transform(embeddings)

# print("clustering")
# c2c = [5,6,7,8]
# labels = dict()
# from sklearn.cluster import AffinityPropagation
# ap = AffinityPropagation()
# for c in c2c:
#     labels[c] = ap.fit_predict([emb for emb,concept 
#                                 in zip(embeddings_transformed,concepts) if concept ==c])
# print(labels)
print("plotting")
import matplotlib.pyplot as plt
import seaborn
#cmap = dict((key,np.random.beta(1,1,3)) for key in cognate_classes)
cmap = dict((key,np.random.beta(1,1,3)) for key in set(concepts))
counters = {5:0,6:0,7:0,8:0}
for language,word,concept,emb in zip(languages,allWords[:2000],concepts,embeddings_transformed):
    plt.annotate(word,emb,
                color=cmap[concept]
                 )
#     if concept == 5:
#         plt.subplot(2,2,1)
#         label = labels[5][counters[5]]
#         plt.annotate(asjp_word+"_"+str(label),emb,color=cmap[cognate_class])
#         counters[5] += 1
#         
#     if concept == 6:
#         plt.subplot(2,2,2)
#         label = labels[6][counters[6]]
#         plt.annotate(asjp_word+"_"+str(label),emb,color=cmap[cognate_class])
#         counters[6] += 1
# 
#     if concept == 7:
#         plt.subplot(2,2,3)
#         label = labels[7][counters[7]]
#         plt.annotate(asjp_word+"_"+str(label),emb,color=cmap[cognate_class])
#         counters[7] += 1
# 
#     if concept == 8:
#         plt.subplot(2,2,4)
#         label = labels[8][counters[8]]
#         plt.annotate(asjp_word+"_"+str(label),emb,color=cmap[cognate_class])
#         counters[8] += 1
        

plt.show()