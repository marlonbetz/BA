

import numpy as np 
from pandas import DataFrame
from gensim.models import Word2Vec
import regex  
import codecs
from scipy.spatial.distance import cosine
from sklearn.neighbors import KNeighborsClassifier
import pickle
def vectorLinspace(start,stop,num=50):
    assert len(start) == len(stop)
    assert num > 0
    return np.array([np.linspace(start[dim],stop[dim],num) for dim in range(len(start))]).transpose()

def getListofASJPPhonemes(word):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    return regex.findall(phonemeSearchRegex, word)

def getWordMatrix(word,model,padToMaxLength = None):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    phonemes = regex.findall(phonemeSearchRegex, word)
    wordVector = []
    for phoneme in phonemes:
        #if phoneme not in model, get single chars as phonemes instead
        if phoneme not in model:
            for ph in regex.findall("["+phonemes_alone+"]", phoneme):
                wordVector.append(model[ph])
        else:       
            wordVector.append(model[phoneme])    
    if padToMaxLength:
        wordVector = wordVector[:padToMaxLength]
        return np.pad(np.array(wordVector),((0,padToMaxLength - len(wordVector)),(0,0)),mode="constant")
    return wordVector

lang_names_IELex_to_ASJP = {
                            "SORBIAN_UPPER":"UPPER_SORBIAN",
                            "IRISH":"IRISH_GAELIC",
                            "GERMAN" : "STANDARD_GERMAN",
                            "ARMENIAN_EASTERN": "EASTERN_ARMENIAN",
                            "OSSETIC_IRON" : "IRON_OSSETIAN",
                            "OSSETIC_DIGOR" : "DIGOR_OSSETIAN",
                            "SERBO-CROATIAN" : "SERBOCROATIAN",
                            "CLASSICAL_ARMENIAN" : "ARMENIAN_CLASSICAL"
                            }
# 
# 
"""
TRAIN PHONEME EMBEDDINGS
"""
print("TRAIN PHONEME EMBEDDINGS")
pathToASJPCorpusFile = "Data/ASJP/dataset.tab"
"""
READ CORPUS FROM ASJP DUMP
"""
print("READ CORPUS FROM ASJP DUMP")
#pathToASJPCorpusFile = "data/dataset.tab"
allWords = []
geo_info = dict()
for i,line in enumerate(codecs.open(pathToASJPCorpusFile,"r","utf-8")):
    if i > 0:
        line = line.split("\t")
        if "PROTO" not in line[0] and "ARTIFICIAL" not in line[2] and "FAKE" not in line[2]:
            words = line[10:]
            #remove invalid characters
            for i,word in enumerate(words):
                words[i] = word.replace("%","")
                words[i] = word.replace(" ","")
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
            geo_info[line[0]] = [float(line[5]),float(line[6])]
    
    
"""
EXTRACT ALL PHONEMES AND ADD WORD BOUNDARIES AND GET RID OF EMPTY STRINGS
"""
print("EXTRACT ALL PHONEMES AND ADD WORD BOUNDARIES AND GET RID OF EMPTY STRINGS")
allWords = [["<s>"]+getListofASJPPhonemes(word)+["</s>"] for word in allWords if len(word) > 0]
 
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
FIT PHONEME EMBEDDING MODEL
"""
 
n_ensemble  =10
sg = 0
hs = 1
dim_embedding = 150
window =1
negative = 0
 
 
print("FIT PHONEME EMBEDDING MODEL")
w2v_model = Word2Vec(sentences=allWords,
                     sg = sg,
                     size=dim_embedding,
                     window=window,
                     negative=negative,
                     hs=hs,
                     min_count=1
                     )

"""
READ WORD LIST
"""
print("READ WORD LIST")
pathToWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

#lists that store info in order of word list file
languages = []
global_ids = []
asjp_words = []
cognate_classes = []

languages_not_in_asjp = set()
c_l = 0
for line in codecs.open(pathToWordList,encoding="utf-8",mode="r"):
    if c_l == 0:
        c_l += 1 
        continue
    line = line.split("\t")
    language = line[0]
    #check if language is proto
    if "PROTO"  in language or "ANCIENT"  in language:
        continue
    #check that language has geo data
    if language not in geo_info:
        if language not in lang_names_IELex_to_ASJP:
            languages_not_in_asjp.add(language)
            continue
        else :
            language = lang_names_IELex_to_ASJP[language]
        
    global_id = line[3]
    asjp_word = line[5]
    asjp_word = asjp_word.replace("%","")
    asjp_word = asjp_word.replace(" ","")
    #check if word exists at all
    if len(asjp_word) ==0:
        continue
    cognate_class = line[6]
    languages.append(language)
    global_ids.append(global_id)
    asjp_words.append(asjp_word)
    cognate_classes.append(cognate_class)

print("languages not contained in asjp")
print(languages_not_in_asjp)
"""
CREATE LANGUAGE ONE HOTS
"""
print("CREATE LANGUAGE ONE HOTS")
language_id = dict((lang,id) for id, lang in enumerate(sorted(list(set(languages)))))
id_language = dict((id,lang) for id, lang in enumerate(sorted(list(set(languages)))))
print(language_id)
print(id_language)

"""
CREATE GLOBAL_ID IDS
"""
print("CREATE GLOBAL_ID")
global_id_id = dict((global_id,id) for id, global_id in enumerate(sorted(list(set(global_ids)))))
id_global_id = dict((id,global_id) for id, global_id in enumerate(sorted(list(set(global_ids)))))

print(global_id_id)
print(id_global_id)


"""
CREATE WORD MATRICES
"""
print("CREATE WORD MATRICES")
padToMaxLength = 15
word_matrices = np.array([getWordMatrix(word, model=w2v_model, padToMaxLength=padToMaxLength).flatten() for word in asjp_words])

"""
CREATE FEEDABLE TRAINING DATA
"""

concepts = np.array([global_id_id[id] for id in global_ids])
concepts_oneHots = []
for concept in concepts:
    tmp = np.zeros(len(global_id_id),dtype=np.bool)
    tmp[concept] = True
    concepts_oneHots.append(tmp)
concepts_oneHots = np.array(concepts_oneHots)
print("languages not contained in asjp")
#print([lang for lang in languages if lang not in geo_info.keys()])
geo_words = np.array([geo_info[lang] for lang in languages])


"""
SCALING GEO DATA
"""
print("SCALING GEO DATA")
from sklearn.preprocessing import MinMaxScaler
minmax_geo  = MinMaxScaler()
geo_words_scaled = minmax_geo.fit_transform(geo_words)

"""
SCALING PHONO DATA
"""
print("SCALING PHONO DATA")
minmax_phono  = MinMaxScaler()
word_matrices_scaled = minmax_phono.fit_transform(word_matrices)
"""
CREATING NETWORK
"""
print("CREATING NETWORK")

from keras.layers import Input, Dense, Lambda,merge,Convolution2D,Reshape,MaxPooling2D,UpSampling2D
from keras.layers.noise import GaussianNoise
from keras.models import Model
from keras import backend as K, objectives
from keras.regularizers import l2


batch_size = 41
original_dim_phono = dim_embedding * padToMaxLength
original_dim_concept = len(global_id_id.keys())
original_dim_geo = 2
latent_dim = 2
intermediate_dim_phono = 1000
intermediate_dim_phono2 = 10000
intermediate_dim_concept = 20
intermediate_dim_geo = 20

epsilon_std = 0.01
nb_epoch = 100
#l2_value = 0.01
l2_value = 0

#encoder concepts

input_concept = Input(batch_shape=(batch_size, original_dim_concept))
h_concept = Dense(intermediate_dim_concept,activation="relu",name="layer_h_concept")(input_concept)

#encoder geo

input_geo = Input(batch_shape=(batch_size, original_dim_geo))
h_geo = Dense(intermediate_dim_geo,activation="relu",name="layer_h_geo")(input_geo)


h_concat = merge([h_concept,h_geo],mode="concat",name="layer_h_concat")
z_mean = Dense(latent_dim,name="z_mean")(h_concat)
z_log_std = Dense(latent_dim,name="z_log_std")(h_concat)

def sampling(args):
    z_mean, z_log_std = args
    epsilon = K.random_normal(shape=(batch_size, latent_dim),
                              mean=0., std=epsilon_std)
    return z_mean + K.exp(z_log_std) * epsilon

z = Lambda(sampling, output_shape=(latent_dim,),name="layer_z")([z_mean, z_log_std])

#decoder phono
# we instantiate these layers separately so as to reuse them later
phono_decoding_layer_intermediate = Dense(intermediate_dim_phono,activation="relu",name="phono_decoding_layer_intermediate")
phono_decoding_intermediate = phono_decoding_layer_intermediate(z)

phono_decoding_layer_intermediate_2 = Dense(intermediate_dim_phono,activation="relu",name="phono_decoding_layer_intermediate_2")
phono_decoding_intermediate_2 = phono_decoding_layer_intermediate_2(phono_decoding_intermediate)

phono_decoding_layer_decoded = Dense(original_dim_phono,activation="sigmoid",name="phono_decoding_layer_decoded")
phono_decoded = phono_decoding_layer_decoded(phono_decoding_intermediate_2)


def vae_loss(input_phono,phono_decoded):
    xent_loss_phono = objectives.binary_crossentropy(input_phono, phono_decoded)

    kl_loss = - 0.5 * K.mean(1 + z_log_std - K.square(z_mean) - K.exp(z_log_std), axis=-1)
    return (
             xent_loss_phono 
             + kl_loss
             )

vae = Model([input_concept,input_geo], [phono_decoded])

"""
COMPILING MODELS
"""
print("COMPILING MODEL")
vae.compile(optimizer='Adam', loss=vae_loss)


"""
FITTING MODELS
"""
print("FITTING MODELS")
print(word_matrices.shape,concepts_oneHots.shape,geo_words.shape)
vae.fit(x=[concepts_oneHots,geo_words_scaled],
         y=[word_matrices_scaled],
      batch_size=batch_size, nb_epoch=nb_epoch)
encoder = Model([input_concept,input_geo], z_mean)
embeddings = encoder.predict(x=[concepts_oneHots,geo_words_scaled],batch_size=batch_size)
encoder_geo = Model([input_geo], h_geo)
embeddings_geo = encoder_geo.predict(x=[geo_words_scaled],batch_size=batch_size)
encoder_concept = Model([input_concept], h_concept)
embeddings_concept = encoder_concept.predict(x=[concepts_oneHots],batch_size=batch_size)
print(embeddings.shape)

"""
WRITING EMBEDDINGS TO PICKLE FILES
"""
print("WRITING EMBEDDINGS TO PICKLE FILES")


pickle.dump(languages,codecs.open("embeddings/local_manifold_learning/langs.pkl","wb"))
pickle.dump(asjp_words,codecs.open("embeddings/local_manifold_learning/asjp_words.pkl","wb"))
pickle.dump(concepts,codecs.open("embeddings/local_manifold_learning/concepts.pkl","wb"))
pickle.dump(concepts_oneHots,codecs.open("embeddings/local_manifold_learning/concepts_oneHots.pkl","wb"))
pickle.dump(geo_words_scaled,codecs.open("embeddings/local_manifold_learning/geo_words_scaled.pkl","wb"))
pickle.dump(cognate_classes,codecs.open("embeddings/local_manifold_learning/cognate_classes.pkl","wb"))


#actual embeddings
pickle.dump(embeddings,codecs.open("embeddings/local_manifold_learning/embeddings.pkl","wb"))
pickle.dump(embeddings_geo,codecs.open("embeddings/local_manifold_learning/embeddings_geo.pkl","wb"))
pickle.dump(embeddings_concept,codecs.open("embeddings/local_manifold_learning/embeddings_concept.pkl","wb"))

if latent_dim != 2:
    
    """
    T-SNE
    """
    print("T-SNE")
    from sklearn.manifold import TSNE
    tsne = TSNE()
    embeddings_tsne = tsne.fit_transform(embeddings)
    print(embeddings_tsne.shape)
    """
    PLOTTING
    """
    print("PLOTTTING")
    cmap_cognateClasses = dict((cognateClass,np.random.beta(1,1,3)) for cognateClass in cognate_classes)
    import matplotlib.pyplot as plt
    print()
    for language,word,emb,cognateClass in zip(languages,asjp_words,embeddings_tsne,cognate_classes):
        plt.annotate(word+"_"+language,(emb[0],emb[1]),color=cmap_cognateClasses[cognateClass],alpha=0.3)
        plt.scatter(emb[0],emb[1],color=cmap_cognateClasses[cognateClass])
    plt.show()
else:
    """
    PLOTTING
    """
    print("PLOTTTING")
    cmap_cognateClasses = dict((cognateClass,np.random.beta(1,1,3)) for cognateClass in cognate_classes)
    import matplotlib.pyplot as plt
    print()
    for language,word,emb,cognateClass in zip(languages,asjp_words,embeddings,cognate_classes):
        plt.annotate(word+"_"+language,(emb[0],emb[1]),color=cmap_cognateClasses[cognateClass],alpha=0.3)
        plt.scatter(emb[0],emb[1],color=cmap_cognateClasses[cognateClass])
    plt.show()
    