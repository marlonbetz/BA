import matplotlib.pyplot as plt
from pipeline import *
from models import VAE


print("READ CORPUS FROM ASJP DUMP")            
pathToASJPCorpusFile = "../../Data/ASJP/dataset.tab"
languages,words,concepts,geo_info = loadASJP(pathToASJPCorpusFile)

print("VECTORIZE TRAINING WORDS")
padToMaxLength = 15
bpf = BinaryPhonemeFeatures()
X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])

print("EMBED WORDS")
padToMaxLength = 15
batch_size = 271
dim_phoneme_embeddings = 16
original_dim = dim_phoneme_embeddings * padToMaxLength
latent_dim = 2
intermediate_dim = 500
epsilon_std = 0.01
nb_epoch =100

vae = VAE(latent_dim=latent_dim,
                          original_dim=original_dim,
                          intermediate_dim=intermediate_dim,
                          batch_size=batch_size,
                          epsilon_std=epsilon_std)

vae.load_weights("../../saved_weights/ASJP_2000/pipeline_asjp_2000.h5")
embeddings = vae.embed(X)

print("plotting")

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

from binary_phoneme_features import BinaryPhonemeFeatures

bpf = BinaryPhonemeFeatures()

cmap = sns.color_palette("hls", len(bpf.labels))


n = len(embeddings)
#n = 4000
bins = dict()
for i,word in enumerate(words[:n]):
    for label in bpf.labels:
        for phoneme in getListofASJPPhonemes(word):
            if bpf.hasFeature(phoneme, label):
                if label not in bins:
                    bins[label] = []
                bins[label].append(i)

for label in bins:
    plt.scatter(embeddings[bins[label],0],embeddings[bins[label],1],color=cmap[bpf.label_id[label]],alpha=0.01,label=label)
#plt.legend(title="word length",frameon=True)
#for word, emb in zip(allWords[:n],embeddings_transformed):
#    l = np.min([15,len(getListofASJPPhonemes(word))])
#    plt.scatter(emb[0],emb[1],alpha=0.1,color=cmap[l-1])   
#plt.scatter(embeddings_transformed[:n,0],embeddings_transformed[:n,1],alpha=0.1)
#seaborn.kdeplot(embeddings_transformed[:n,0],embeddings_transformed[:n,1])
        

plt.show()