from pipeline import *


print("READ CORPUS FROM ASJP DUMP")            
pathToASJPCorpusFile = "Data/ASJP/dataset.tab"
languages_train,words_train,concepts_train,geo_info_train = loadASJP(pathToASJPCorpusFile)

print("VECTORIZE TRAINING WORDS")
padToMaxLength = 15
bpf = BinaryPhonemeFeatures()
X_train = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words_train])

print("shape of X:",X_train.shape)

print("FIT VAE")

batch_size = 271
dim_phoneme_embeddings = 16
original_dim = dim_phoneme_embeddings * padToMaxLength
latent_dim = 2
intermediate_dim = 500


epsilon_std = 0.01
nb_epoch =50

vae = VAE(latent_dim=latent_dim,
          original_dim=original_dim,
          intermediate_dim=intermediate_dim,
          batch_size=batch_size,
          epsilon_std=epsilon_std)

vae.fit(X_train,
      nb_epoch=nb_epoch)

print("LOAD TEST WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages_test,words_test,global_ids_test,cognate_classes_test = loadAnnotatedWordList(pathToAnnotatedWordList, None)

print("VECTORIZE TEST WORDS")
X_test = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words_test])

print("EMBED TEST WORDS")
embeddings_test = vae.embed(X_test)

print("CLUSTER WORDS OF EVERY CONCEPT")
concepts2embeddings_test = dict((concept,[emb for i,emb in enumerate(embeddings_test) if global_ids_test[i] == concept]) for concept in set(sorted(global_ids_test)))
concepts2cognate_classes_test = dict((concept,[cog for i,cog in enumerate(cognate_classes_test) if global_ids_test[i] == concept]) for concept in set(sorted(global_ids_test)))
ap = AffinityPropagation()
scores_adjusted_rand_score = []
scores_adjusted_rand_score_random = []
scores_adjusted_mutual_info_score = []
scores_adjusted_mutual_info_score_random = []
n_cognate_classes = len(set(cognate_classes_test))
n_concepts = len(set(global_ids_test))
for concept in concepts2embeddings_test:
    y_true = concepts2cognate_classes_test[concept]
    y_pred = ap.fit_predict(concepts2embeddings_test[concept])
    y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)
    scores_adjusted_rand_score.append(metrics.adjusted_rand_score(y_true, y_pred))
    scores_adjusted_mutual_info_score.append(metrics.adjusted_mutual_info_score(y_true, y_pred))
    
    scores_adjusted_rand_score_random.append(metrics.adjusted_rand_score(y_true, y_random))
    scores_adjusted_mutual_info_score_random.append(metrics.adjusted_mutual_info_score(y_true, y_random))

print(np.mean(scores_adjusted_rand_score))
print(np.mean(scores_adjusted_mutual_info_score))
print(np.mean(scores_adjusted_rand_score_random))
print(np.mean(scores_adjusted_mutual_info_score_random))
