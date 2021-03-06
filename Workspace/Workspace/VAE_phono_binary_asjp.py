

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

# 
# """
# READ WORD LIST
# """
# print("READ WORD LIST")
# pathToWordList = "Data/IELex/output/IELex-2016.tsv.asjp"
# 
# #concepts to train
# c2t = {}
# #lists that store info in order of word list file
# languages = []
# global_ids = []
# asjp_words = []
# cognate_classes = []
# c_l = 0
# languages_not_in_asjp = set()
# 
# for line in codecs.open(pathToWordList,encoding="utf-8",mode="r"):
#     if c_l == 0:
#         c_l += 1 
#         continue
#     line = line.split("\t")
#     language = line[0]
#     #check if language is proto
#     if "PROTO"  in language or "ANCIENT"  in language:
#         continue
#     #check that language has geo data
#     if language not in geo_info:
#         if language not in lang_names_IELex_to_ASJP:
#             languages_not_in_asjp.add(language)
#             continue
#         else :
#             language = lang_names_IELex_to_ASJP[language]
#     global_id = int(line[3])
#     #check that concept is in c2t, if c2t is empty ignore c2t
#     if global_id not in c2t and len(c2t) != 0:
#         continue
#     asjp_word = line[5]
#     asjp_word = asjp_word.replace("%","")
#     asjp_word = asjp_word.replace(" ","")
#     #check if word exists at all
#     if len(asjp_word) ==0:
#         continue
#     cognate_class = line[6]
#     languages.append(language)
#     global_ids.append(global_id)
#     asjp_words.append(asjp_word)
#     cognate_classes.append(cognate_class)
# print("languages not contained in asjp")
# print(languages_not_in_asjp)
# """
# CREATE LANGUAGE ONE HOTS
# """
# print("CREATE LANGUAGE ONE HOTS")
# language_id = dict((lang,id) for id, lang in enumerate(sorted(list(set(languages)))))
# id_language = dict((id,lang) for id, lang in enumerate(sorted(list(set(languages)))))
# print(language_id)
# print(id_language)
# 
# """
# CREATE GLOBAL_ID IDS
# """
# print("CREATE GLOBAL_ID")
# global_id_id = dict((global_id,id) for id, global_id in enumerate(sorted(list(set(global_ids)))))
# id_global_id = dict((id,global_id) for id, global_id in enumerate(sorted(list(set(global_ids)))))
# 
# print(global_id_id)
# print(id_global_id)


"""
CREATE WORD MATRICES
"""
print("CREATE WORD MATRICES")
padToMaxLength = 15
from binary_phoneme_features import BinaryPhonemeFeatures
bpf  =BinaryPhonemeFeatures()

word_matrices = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in allWords])
"""
CREATE FEEDABLE TRAINING DATA
"""
# 
# concepts = np.array([global_id_id[id] for id in global_ids])
# concepts_oneHots = []
# for concept in concepts:
#     tmp = np.zeros(len(global_id_id),dtype=np.bool)
#     tmp[concept] = True
#     concepts_oneHots.append(tmp)
# concepts_oneHots = np.array(concepts_oneHots)
# print("languages not contained in asjp")
# print([lang for lang in languages if lang not in geo_info.keys()])
# geo_words = np.array([geo_info[lang] for lang in languages])




"""
CREATING NETWORK
"""
print("CREATING NETWORK")



from models import VAE

batch_size = 271
dim_phoneme_embeddings = 16
original_dim_phono = dim_phoneme_embeddings * padToMaxLength
latent_dim = 2
intermediate_dim_phono = 500


epsilon_std = 0.01
nb_epoch = 100

vae = VAE(latent_dim=latent_dim,
          original_dim=original_dim_phono,
          intermediate_dim=intermediate_dim_phono,
          batch_size=batch_size,
          epsilon_std=epsilon_std)


"""
FITTING MODELS
"""
print("FITTING MODELS")
print(word_matrices.shape,
      #concepts_oneHots.shape,geo_words.shape
      )
vae.fit(word_matrices,
      nb_epoch=nb_epoch)
embeddings = vae.embed(X=word_matrices)

print(embeddings.shape)

"""
WRITING EMBEDDINGS TO PICKLE FILES
"""
print("WRITING EMBEDDINGS TO PICKLE FILES")


#pickle.dump(languages,codecs.open("embeddings/vae_phono_binary/langs.pkl","wb"))
#pickle.dump(asjp_words,codecs.open("embeddings/vae_phono_binary/asjp_words.pkl","wb"))
#pickle.dump(concepts,codecs.open("embeddings/vae_phono_binary/concepts.pkl","wb"))
#pickle.dump(concepts_oneHots,codecs.open("embeddings/vae_phono_binary/concepts_oneHots.pkl","wb"))
pickle.dump(word_matrices,codecs.open("embeddings/vae_phono_binary_asjp/word_matrices.pkl","wb"))
#pickle.dump(cognate_classes,codecs.open("embeddings/vae_phono_binary/cognate_classes.pkl","wb"))
pickle.dump(allWords,codecs.open("embeddings/vae_phono_binary_asjp/allWords.pkl","wb"))


#actual embeddings
pickle.dump(embeddings,codecs.open("embeddings/vae_phono_binary_asjp/embeddings.pkl","wb"))
# 
# if latent_dim != 2:
#     
#     """
#     T-SNE
#     """
#     print("T-SNE")
#     from sklearn.manifold import TSNE
#     tsne = TSNE()
#     embeddings_tsne = tsne.fit_transform(embeddings)
#     print(embeddings_tsne.shape)
#     """
#     PLOTTING
#     """
#     print("PLOTTTING")
#     #cmap_cognateClasses = dict((cognateClass,np.random.beta(1,1,3)) for cognateClass in cognate_classes)
#     import matplotlib.pyplot as plt
#     print()
#     for word,emb in zip(allWords,embeddings_tsne):
#         plt.annotate(word
#                      #+"_"+language
#                      ,
#                      (emb[0],emb[1]),
#                      #color=cmap_cognateClasses[cognateClass],
#                      alpha=0.3)
#         plt.scatter(emb[0],emb[1],
#                     #color=cmap_cognateClasses[cognateClass]
#                     )
#     plt.show()
# else:
#     """
#     PLOTTING
#     """
#     print("PLOTTTING")
#     #cmap_cognateClasses = dict((cognateClass,np.random.beta(1,1,3)) for cognateClass in cognate_classes)
#     import matplotlib.pyplot as plt
#     print()
#     for word,emb in zip(allWords,embeddings):
#         plt.annotate(word
#                      #+"_"+language
#                      ,
#                      (emb[0],emb[1]),
#                      #color=cmap_cognateClasses[cognateClass],
#                      alpha=0.3)
#         plt.scatter(emb[0],emb[1],
#                     #color=cmap_cognateClasses[cognateClass]
#                     )
#     plt.show()
#     