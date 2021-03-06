import numpy as np
import regex
import codecs
from binary_phoneme_features import BinaryPhonemeFeatures
from phoneme_embeddings import PhonemeEmbeddings
from models import VAE
from sklearn.cluster import AffinityPropagation
from sklearn import metrics

def getRidOfValidationSet(languages,words,global_ids,cognate_classes,stoplist):
    indices = []
    for i,id in enumerate(global_ids):
        if id not in stoplist:
            indices.append(i)
    return np.array(languages)[indices],np.array(words)[indices],np.array(global_ids)[indices],np.array(cognate_classes)[indices]

def getListofASJPPhonemes(word):
    phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
    phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
    return regex.findall(phonemeSearchRegex, word)

def loadASJP(pathToASJPCorpusFile):
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
    return languages,allWords,concepts,geo_info

def loadAnnotatedWordList(pathToWordList,concepts_to_include=None):
    
    #concepts to include
    if not concepts_to_include:
        concepts_to_include = {}
    else:
        concepts_to_include = set(concepts_to_include)
               
    #lists that store info in order of word list file
    languages = []
    global_ids = []
    words = []
    cognate_classes = []
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
        global_id = int(line[3])
        #check that concept is in concepts_to_include, if concepts_to_include is empty ignore concepts_to_include
        if global_id not in concepts_to_include and len(concepts_to_include) != 0:
            continue
        word = line[5]
        word = word.replace("%","")
        word = word.replace(" ","")
        #check if word exists at all
        if len(word) ==0:
            continue
        cognate_class = line[6]
        
        languages.append(language)
        global_ids.append(global_id)
        words.append(word)
        cognate_classes.append(cognate_class)
        
    return languages,words,global_ids,cognate_classes
# 
# print("READ CORPUS FROM ASJP DUMP")            
# pathToASJPCorpusFile = "Data/ASJP/dataset.tab"
# languages_train,words_train,concepts_train,geo_info_train = loadASJP(pathToASJPCorpusFile)
# 
# print("VECTORIZE TRAINING WORDS")
# padToMaxLength = 15
# bpf = BinaryPhonemeFeatures()
# X_train = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words_train])
# 
# print("shape of X:",X_train.shape)
# 
# print("FIT VAE")
# 
# batch_size = 271
# dim_phoneme_embeddings = 16
# original_dim = dim_phoneme_embeddings * padToMaxLength
# latent_dim = 2
# intermediate_dim = 500
# 
# 
# epsilon_std = 0.01
# nb_epoch =50
# 
# vae = VAE(latent_dim=latent_dim,
#           original_dim=original_dim,
#           intermediate_dim=intermediate_dim,
#           batch_size=batch_size,
#           epsilon_std=epsilon_std)
# 
# vae.fit(X_train,
#       nb_epoch=nb_epoch)
# 
# print("LOAD TEST WORDLIST")
# pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"
# 
# languages_test,words_test,global_ids_test,cognate_classes_test = loadAnnotatedWordList(pathToAnnotatedWordList, None)
# 
# print("VECTORIZE TEST WORDS")
# X_test = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words_test])
# 
# print("EMBED TEST WORDS")
# embeddings_test = vae.embed(X_test)
# 
# print("CLUSTER WORDS OF EVERY CONCEPT")
# concepts2embeddings_test = dict((concept,[emb for i,emb in enumerate(embeddings_test) if global_ids_test[i] == concept]) for concept in set(sorted(global_ids_test)))
# concepts2cognate_classes_test = dict((concept,[cog for i,cog in enumerate(cognate_classes_test) if global_ids_test[i] == concept]) for concept in set(sorted(global_ids_test)))
# ap = AffinityPropagation()
# scores_adjusted_rand_score = []
# scores_adjusted_rand_score_random = []
# scores_adjusted_mutual_info_score = []
# scores_adjusted_mutual_info_score_random = []
# n_cognate_classes = len(set(cognate_classes_test))
# n_concepts = len(set(global_ids_test))
# for concept in concepts2embeddings_test:
#     y_true = concepts2cognate_classes_test[concept]
#     y_pred = ap.fit_predict(concepts2embeddings_test[concept])
#     y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)
#     scores_adjusted_rand_score.append(metrics.adjusted_rand_score(y_true, y_pred))
#     scores_adjusted_mutual_info_score.append(metrics.adjusted_mutual_info_score(y_true, y_pred))
#     
#     scores_adjusted_rand_score_random.append(metrics.adjusted_rand_score(y_true, y_random))
#     scores_adjusted_mutual_info_score_random.append(metrics.adjusted_mutual_info_score(y_true, y_random))
# 
# print(np.mean(scores_adjusted_rand_score))
# print(np.mean(scores_adjusted_mutual_info_score))
# print(np.mean(scores_adjusted_rand_score_random))
# print(np.mean(scores_adjusted_mutual_info_score_random))
