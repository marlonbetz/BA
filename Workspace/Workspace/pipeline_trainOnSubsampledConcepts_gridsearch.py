from pipeline import *
from lingpy import  *

n_subsamples = 10
phoneme_vectorizations = ["dolgo","sca","binary","embeddings"]
latent_dims = np.array([10,20,50])
epsilon_stds = np.array([0.1,0.01,0.001])
n_ensemble = 1
nb_epoch = 4000
intermediate_dim = 1000

print("LOAD WORDLIST TO SAMPLE FROM")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList)

pathToAnnotatedWordList_ipa = "Data/IELex/output/IELex-2016.tsv"

_,words_ipa,_,_ = loadAnnotatedWordList(pathToAnnotatedWordList_ipa)


global_id_types = np.array(list(set(global_ids)))
print(len(global_id_types))
global_id_types_subset = np.random.choice(global_id_types, n_subsamples, replace=False)
print("global_id_types_subset")
print(global_id_types_subset)
del languages,words,global_ids,cognate_classes

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList,set(global_id_types_subset))
print(len(words))
print("VECTORIZE WORDS WITH BINARY FEATURES")
X_dict = dict()
padToMaxLength=10
bpf = BinaryPhonemeFeatures()
X_dict["binary"] = dict((concept,np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word,concept_tmp in zip(words,global_ids) if  concept_tmp == concept]))for concept in global_ids)

print("VECTORIZE WORDS WITH PHONEME EMBEDDINGS")
dim_phoneme_embeddings = 20
pe = PhonemeEmbeddings(pathToASJPCorpusFile = "Data/ASJP/dataset.tab",
                       ignoreCoarticulations=True,
                        sg = 0, 
                        size = dim_phoneme_embeddings, 
                        window = 1, 
                        negative = 0, 
                        hs = 1, 
                        min_count=1)

from sklearn.preprocessing import MinMaxScaler
minmax = MinMaxScaler()

X_dict["embeddings"] = dict(
                 (concept,
                  (np.array(minmax.fit_transform([pe.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word,concept_tmp in zip(words,global_ids) if  concept_tmp == concept])))
                                    )
                 for concept in global_ids)

print("VECTORIZE WORDS WITH DOLGOPOLSKY FEATURES")
from SoundClassFeatures import SoundClassFeatures
scf_dolgo = SoundClassFeatures("dolgo")

X_dict["dolgo"] = dict(
                 (concept,
                  (np.array([scf_dolgo.encodeWordToOneHots(word, padToMaxLength=padToMaxLength).flatten() for word,concept_tmp in zip(words_ipa,global_ids) if  concept_tmp == concept]))
                                    )
                 for concept in global_ids)
concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))


print("VECTORIZE WORDS WITH SCA FEATURES")
scf_sca = SoundClassFeatures("sca")

X_dict["sca"] = dict(
                 (concept,
                  (np.array([scf_sca.encodeWordToOneHots(word, padToMaxLength=padToMaxLength).flatten() for word,concept_tmp in zip(words_ipa,global_ids) if  concept_tmp == concept]))
                                    )
                 for concept in global_ids)
concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))


n_cognate_classes_true_perDataPoint = []
n_cognate_classes_pred_perDataPoint = []

adjusted_rand_scores = np.zeros((len(phoneme_vectorizations),len(latent_dims),len(epsilon_stds),n_subsamples,n_ensemble))
adjusted_mutual_info_scores = np.zeros((len(phoneme_vectorizations),len(latent_dims),len(epsilon_stds),n_subsamples,n_ensemble))
homogeneity_scores = np.zeros((len(phoneme_vectorizations),len(latent_dims),len(epsilon_stds),n_subsamples,n_ensemble))
completeness_scores = np.zeros((len(phoneme_vectorizations),len(latent_dims),len(epsilon_stds),n_subsamples,n_ensemble))
v_measure_scores = np.zeros((len(phoneme_vectorizations),len(latent_dims),len(epsilon_stds),n_subsamples,n_ensemble))


import pickle
import codecs
pickle.dump(adjusted_rand_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/adjusted_rand_scores_new.pkl","wb"))                        
pickle.dump(adjusted_mutual_info_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/adjusted_mutual_info_scores_new.pkl","wb"))                        
pickle.dump(homogeneity_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/homogeneity_scores_new.pkl","wb"))                        
pickle.dump(completeness_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/completeness_scores_new.pkl","wb"))                        
pickle.dump(v_measure_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/v_measure_scores_new.pkl","wb"))     

for i_phoneme_vectorization, phoneme_vectorization in enumerate(phoneme_vectorizations):
    for i_ld, latent_dim in enumerate(latent_dims):
        for i_epsilon_std, epsilon_std in enumerate(epsilon_stds):
            for i_concept,(concept,X) in enumerate(X_dict[phoneme_vectorization].items()):
                for n_tmp in range(n_ensemble):
                    print(i_phoneme_vectorization,i_ld,i_epsilon_std,i_concept,n_tmp)
                    print("FIT VAE")
                    #print(concept,X)
                    batch_size = X.shape[0]
                    
                    if phoneme_vectorization == "binary":
                        dim_phoneme_vectorization = 16
                    elif phoneme_vectorization == "embeddings":
                        dim_phoneme_vectorization = 20
                    elif phoneme_vectorization == "dolgo":
                        dim_phoneme_vectorization = scf_dolgo.n_classes
                    elif phoneme_vectorization == "sca":
                        dim_phoneme_vectorization = scf_sca.n_classes
                    
                    original_dim = dim_phoneme_vectorization * padToMaxLength
                     
                     
                    epsilon_std = 0.1
                     
                    vae = VAE(latent_dim=latent_dim,
                              original_dim=original_dim,
                              intermediate_dim=intermediate_dim,
                              batch_size=batch_size,
                              epsilon_std=epsilon_std)
                    vae.fit(X,
                          nb_epoch=nb_epoch)
                     
                     
                    print("EMBED TEST WORDS")
                    embeddings = vae.embed(X)
                     
                    print("CLUSTER WORDS")
                 
                    ap = AffinityPropagation()
                    n_cognate_classes = len(set(cognate_classes))
                    n_concepts = len(set(global_ids))
                    y_true = concepts2cognate_classes[concept]
                    y_pred = ap.fit_predict(embeddings)
                                             
                    ars = metrics.adjusted_rand_score(y_true, y_pred)
                    ami = metrics.adjusted_mutual_info_score(y_true, y_pred)
                    homo,compl,v = metrics.homogeneity_completeness_v_measure(y_true, y_pred)
                    print(ars,ami,homo,compl,v)
                    
                    adjusted_rand_scores[(i_phoneme_vectorization,i_ld,i_epsilon_std,i_concept,n_tmp)] = ars
                    adjusted_mutual_info_scores[(i_phoneme_vectorization,i_ld,i_epsilon_std,i_concept,n_tmp)] = ami
                    homogeneity_scores[(i_phoneme_vectorization,i_ld,i_epsilon_std,i_concept,n_tmp)] = homo
                    completeness_scores[(i_phoneme_vectorization,i_ld,i_epsilon_std,i_concept,n_tmp)] = compl
                    v_measure_scores[(i_phoneme_vectorization,i_ld,i_epsilon_std,i_concept,n_tmp)] = v
import pickle
import codecs
pickle.dump(adjusted_rand_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/adjusted_rand_scores_new.pkl","wb"))                        
pickle.dump(adjusted_mutual_info_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/adjusted_mutual_info_scores_new.pkl","wb"))                        
pickle.dump(homogeneity_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/homogeneity_scores_new.pkl","wb"))                        
pickle.dump(completeness_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/completeness_scores_new.pkl","wb"))                        
pickle.dump(v_measure_scores,codecs.open("pickled_stuff/pipeline_trainOnSubsampledConcepts_gridsearch/v_measure_scores_new.pkl","wb"))                        
