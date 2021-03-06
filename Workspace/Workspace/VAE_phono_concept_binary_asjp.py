

import numpy as np 
from pandas import DataFrame
from gensim.models import Word2Vec
import regex  
import codecs
from scipy.spatial.distance import cosine
from sklearn.neighbors import KNeighborsClassifier
import pickle
import sys
def vectorLinspace(start,stop,num=50):
    assert len(start) == len(stop)
    assert num > 0
    return np.array([np.linspace(start[dim],stop[dim],num) for dim in range(len(start))]).transpose()

def getListofASJPPhonemes(word):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    return regex.findall(phonemeSearchRegex, word)

def encodeWord(word,model,padToMaxLength = None):
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





"""
READ CORPUS FROM ASJP DUMP
"""
print("READ CORPUS FROM ASJP DUMP")
pathToASJPCorpusFile = "Data/ASJP/dataset.tab"

allWords = []
geo_info = []
concepts = []
languages = []
for i,line in enumerate(codecs.open(pathToASJPCorpusFile,"r","utf-8")):
    if i > 0:
        line = line.split("\t")
        if "PROTO" not in line[0] and "ARTIFICIAL" not in line[2] and "FAKE" not in line[2]:
            words_tmp = line[10:]
            #remove invalid characters
            for i,word in enumerate(words_tmp):
                words_tmp[i] = words_tmp[i].replace("%","")
                words_tmp[i] = words_tmp[i].replace(" ","")              
                words_tmp[i] = words_tmp[i].replace("\r","")
                words_tmp[i] = words_tmp[i].replace("\n","")

            for i_w,word in enumerate(words_tmp):
                if len(getListofASJPPhonemes(word)) > 0:
                    
                                
                    """
                    for cells with more than one corresponding word, only take first one
                    """
                    if "," in word:
                        word_splitted = word.split(",")
                        if len(getListofASJPPhonemes(word_splitted[0])) > 0:
                            
                            allWords.append(word_splitted[0])
                        else:
                            allWords.append(word_splitted[1])
                    else:
                        allWords.append(word)
                    
                    concepts.append(i_w)
                    geo_info.append([float(line[5]),float(line[6])])
                    languages.append(line[0])
                    

print(len(languages))
print(len(allWords))
print(len(concepts))
print(len(geo_info))
print(geo_info[0])


"""
CREATE CONCEPT IDS
"""
print("CREATE CONCEPT IDS")
concept_id = dict((concept,id) for id, concept in enumerate(sorted(list(set(concepts)))))
id_concept = dict((id,concept) for id, concept in enumerate(sorted(list(set(concepts)))))
 
print(concept_id)
print(id_concept)



"""
CREATE WORD MATRICES
"""
print("CREATE WORD MATRICES")
padToMaxLength = 15
from binary_phoneme_features import BinaryPhonemeFeatures
bpf  =BinaryPhonemeFeatures()

word_matrices = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in allWords])
"""
CREATE CONCEPT ONE HOTS
"""
print("CREATE CONCEPT ONE HOTS")

concepts_oneHots = []
for concept in concepts:
    tmp = np.zeros(len(concept_id),dtype=np.bool)
    tmp[concept] = True
    concepts_oneHots.append(tmp)
concepts_oneHots = np.array(concepts_oneHots)

"""
CONCATENATE PHONO DATA WITH CONCEPT ONE HOTS
"""
print("CONCATENATE PHONO DATA WITH CONCEPT ONE HOTS")

X = np.append(word_matrices,concepts_oneHots,axis=1)
print("shape of X:",X.shape)
"""
CREATING NETWORK
"""
print("CREATING NETWORK")



from models import VAE

batch_size = 271
dim_phoneme_embeddings = 16
original_dim = X.shape[1]
latent_dim = 2
intermediate_dim = 500


epsilon_std = 0.01
nb_epoch = 1000

vae = VAE(latent_dim=latent_dim,
          original_dim=original_dim,
          intermediate_dim=intermediate_dim,
          batch_size=batch_size,
          epsilon_std=epsilon_std)


"""
FITTING MODELS
"""
print("FITTING MODELS")
print(word_matrices.shape,
      #concepts_oneHots.shape,geo_words.shape
      )
vae.fit(X,
      nb_epoch=nb_epoch)
embeddings = vae.embed(X=X)

print(embeddings.shape)

"""
WRITING EMBEDDINGS TO PICKLE FILES
"""
print("WRITING EMBEDDINGS TO PICKLE FILES")



pickle.dump(languages,codecs.open("embeddings/vae_phono_concept_binary_asjp/languages.pkl","wb"))
pickle.dump(allWords,codecs.open("embeddings/vae_phono_concept_binary_asjp/allWords.pkl","wb"))
pickle.dump(concepts,codecs.open("embeddings/vae_phono_concept_binary_asjp/concepts.pkl","wb"))
pickle.dump(geo_info,codecs.open("embeddings/vae_phono_concept_binary_asjp/geo_info.pkl","wb"))

#actual embeddings
pickle.dump(embeddings,codecs.open("embeddings/vae_phono_concept_binary_asjp/embeddings.pkl","wb"))
