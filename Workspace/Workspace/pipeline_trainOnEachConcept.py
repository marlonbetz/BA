from pipeline import *
import pickle
from pairwise_evaluation import PairwiseEvaluation
n_ensemble = 1

stoplist = {221 , 646 ,1333 ,1224 , 778 ,1402, 1411, 1232, 1203, 1292}
def getRidOfValidationSet(languages,words,global_ids,cognate_classes,stoplist):
    indices = []
    for i,id in enumerate(global_ids):
        if id not in stoplist:
            indices.append(i)
    return np.array(languages)[indices],np.array(words)[indices],np.array(global_ids)[indices],np.array(cognate_classes)[indices]
print("LOAD WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"
#pathToAnnotatedWordList = "Data/mattis_new/output/ObUgrian-110-21.tsv.asjp"
languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList)
print(len(set(global_ids)))
languages,words,global_ids,cognate_classes = getRidOfValidationSet(languages,words,global_ids,cognate_classes,stoplist)
print(len(set(global_ids)))

print("VECTORIZE WORDS")
padToMaxLength=10
bpf = BinaryPhonemeFeatures()

print("X dict")
X_dict = dict((concept,np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word,concept_tmp in zip(words,global_ids) if  concept_tmp == concept]))for concept in global_ids)
print("concepts2cognate_classes")
concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))

print("concepts2words")
concepts2words = dict((concept,np.array([word for word,concept_tmp in zip(words,global_ids) if  concept_tmp == concept]))for concept in global_ids)
print("lang dict")
concepts2langs = dict((concept,np.array([lang for lang,concept_tmp in zip(languages,global_ids) if  concept_tmp == concept]))for concept in global_ids)
pickle.dump(concepts2words,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/concepts2words.pkl","wb"))
pickle.dump(concepts2langs,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/concepts2langs.pkl","wb"))
print("deleting those")
del concepts2words,concepts2langs
concepts2embeddings =  dict((concept,[])for concept in global_ids)
concepts2y_pred =  dict((concept,[])for concept in global_ids)

adjusted_rand_scores =  np.zeros((len(concepts2cognate_classes),n_ensemble))
adjusted_mutual_info_scores  =np.zeros((len(concepts2cognate_classes),n_ensemble))
homogeneity_scores = np.zeros((len(concepts2cognate_classes),n_ensemble))
completeness_scores = np.zeros((len(concepts2cognate_classes),n_ensemble))
v_measures_scores = np.zeros((len(concepts2cognate_classes),n_ensemble))
pairwise_precision =  np.zeros((len(concepts2cognate_classes),n_ensemble))
pairwise_recall = np.zeros((len(concepts2cognate_classes),n_ensemble))
pairwise_f1 = np.zeros((len(concepts2cognate_classes),n_ensemble))
n_cognate_classes_true_perDataPoint = np.zeros((len(concepts2cognate_classes),n_ensemble))
n_cognate_classes_pred_perDataPoint = np.zeros((len(concepts2cognate_classes),n_ensemble))

adjusted_rand_scores_random =  np.zeros((len(concepts2cognate_classes),n_ensemble))
adjusted_mutual_info_scores_random  =np.zeros((len(concepts2cognate_classes),n_ensemble))
homogeneity_scores_random = np.zeros((len(concepts2cognate_classes),n_ensemble))
completeness_scores_random = np.zeros((len(concepts2cognate_classes),n_ensemble))
v_measures_scores_random = np.zeros((len(concepts2cognate_classes),n_ensemble))

pairwise_precision_random =  np.zeros((len(concepts2cognate_classes),n_ensemble))
pairwise_recall_random = np.zeros((len(concepts2cognate_classes),n_ensemble))
pairwise_f1_random = np.zeros((len(concepts2cognate_classes),n_ensemble))
# pickle.dump(adjusted_rand_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/adjusted_rand_scores.pkl","wb"))
# pickle.dump(adjusted_mutual_info_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/adjusted_mutual_info_scores.pkl","wb"))
# pickle.dump(homogeneity_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/homogeneity_scores.pkl","wb"))
# pickle.dump(completeness_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/completeness_scores.pkl","wb"))
# pickle.dump(v_measures_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/v_measures_scores.pkl","wb"))
# 
# pickle.dump(adjusted_rand_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/adjusted_rand_scores_random.pkl","wb"))
# pickle.dump(adjusted_mutual_info_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/adjusted_mutual_info_scores_random.pkl","wb"))
# pickle.dump(homogeneity_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/homogeneity_scores_random.pkl","wb"))
# pickle.dump(completeness_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/completeness_scores_random.pkl","wb"))
# pickle.dump(v_measures_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/v_measures_scores_random.pkl","wb"))
# pickle.dump(n_cognate_classes_true_perDataPoint,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/n_cognate_classes_true_perDataPoint.pkl","wb"))
# pickle.dump(n_cognate_classes_pred_perDataPoint,codecs.open("pickled_stuff/pipeline_trainOnEachConcept/n_cognate_classes_pred_perDataPoint.pkl","wb"))

n_concepts = len(X_dict.keys())
print("n_concepts",n_concepts)
for i,item in enumerate(X_dict.items()):
    for n in range(n_ensemble):
        print(i,"/",n_concepts,n,"/",n_ensemble)
        concept,X  = item
        print("FIT VAE")
        
        batch_size = X.shape[0]
        dim_phoneme_embeddings = 16
        original_dim = dim_phoneme_embeddings * padToMaxLength
        latent_dim = 10
        intermediate_dim = 1000
        
        
        epsilon_std = 0.1
        nb_epoch =8000
        
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
        #for damping_factor in np.arange(0.5,1,0.05):
    
        damping_factor = 0.5
        ap = AffinityPropagation(damping=damping_factor)
        n_cognate_classes = len(set(cognate_classes))
        n_concepts = len(set(global_ids))
        y_true = concepts2cognate_classes[concept]
        y_pred = ap.fit_predict(embeddings)
        y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)
        

        ars = metrics.adjusted_rand_score(y_true, y_pred)
        ami = metrics.adjusted_mutual_info_score(y_true, y_pred)
        h,c,v = metrics.homogeneity_completeness_v_measure(y_true, y_pred)
        pe = PairwiseEvaluation(X,y_true,y_pred)
        precision,recall,f1 = pe.getPrecisionRecallF1()
        adjusted_rand_scores[i,n] = ars
        adjusted_mutual_info_scores[i,n] = ami
        homogeneity_scores[i,n] = h
        completeness_scores[i,n] = c
        v_measures_scores[i,n] = v
        pairwise_precision[i,n] = precision
        pairwise_recall[i,n] = recall
        pairwise_f1[i,n] = f1
        
        ars_random = metrics.adjusted_rand_score(y_true, y_random)
        ami_random = metrics.adjusted_mutual_info_score(y_true, y_random)
        h_random,c_random,v_random = metrics.homogeneity_completeness_v_measure(y_true, y_random)
        pe_random = PairwiseEvaluation(X,y_true,y_random)
        precision_random,recall_random,f1_random = pe_random.getPrecisionRecallF1()
        adjusted_rand_scores_random[i,n] = ars_random
        adjusted_mutual_info_scores_random[i,n] = ami_random
        homogeneity_scores_random[i,n] = h_random
        completeness_scores_random[i,n] = c_random
        v_measures_scores_random[i,n] = v_random
        pairwise_precision_random[i,n] = precision_random
        pairwise_recall_random[i,n] = recall_random
        pairwise_f1_random[i,n] = f1_random
        
        concepts2embeddings[concept].extend(embeddings)
        concepts2y_pred[concept].extend(y_pred)
        print(ars,ami,h,c,v,precision,recall,f1)
        print(ars_random,ami_random,h_random,c_random,v_random,precision_random,recall_random,f1_random)

        
        n_cognate_classes_true_tmp =  len(set(concepts2cognate_classes[concept]))
        n_cognate_classes_pred_tmp =  len(set(y_pred))
        print("estimated number of cognate classes",n_cognate_classes_pred_tmp)
        print("true number of cognate classes",n_cognate_classes_true_tmp)
        n_cognate_classes_true_perDataPoint[i,n] = n_cognate_classes_true_tmp
        n_cognate_classes_pred_perDataPoint[i,n] = n_cognate_classes_pred_tmp
        


print("adjusted_rand_scores",np.mean(adjusted_rand_scores))
print("adjusted_mutual_info_scores",np.mean(adjusted_mutual_info_scores))
print("homogeneity_scores",np.mean(np.array(homogeneity_scores)))
print("completeness_scores",np.mean(np.array(completeness_scores)))
print("v_measures_scores",np.mean(np.array(v_measures_scores)))

pickle.dump(adjusted_rand_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/adjusted_rand_scores.pkl","wb"))
pickle.dump(adjusted_mutual_info_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/adjusted_mutual_info_scores.pkl","wb"))
pickle.dump(homogeneity_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/homogeneity_scores.pkl","wb"))
pickle.dump(completeness_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/completeness_scores.pkl","wb"))
pickle.dump(v_measures_scores,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/v_measures_scores.pkl","wb"))
pickle.dump(pairwise_precision,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/pairwise_precision.pkl","wb"))
pickle.dump(pairwise_recall,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/pairwise_recall.pkl","wb"))
pickle.dump(pairwise_f1,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/pairwise_f1.pkl","wb"))


pickle.dump(adjusted_rand_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/adjusted_rand_scores_random.pkl","wb"))
pickle.dump(adjusted_mutual_info_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/adjusted_mutual_info_scores_random.pkl","wb"))
pickle.dump(homogeneity_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/homogeneity_scores_random.pkl","wb"))
pickle.dump(completeness_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/completeness_scores_random.pkl","wb"))
pickle.dump(v_measures_scores_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/v_measures_scores_random.pkl","wb"))
pickle.dump(pairwise_precision_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/pairwise_precision_random.pkl","wb"))
pickle.dump(pairwise_recall_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/pairwise_recall_random.pkl","wb"))
pickle.dump(pairwise_f1_random,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/pairwise_f1_random.pkl","wb"))



pickle.dump(n_cognate_classes_true_perDataPoint,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/n_cognate_classes_true_perDataPoint.pkl","wb"))
pickle.dump(n_cognate_classes_pred_perDataPoint,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/n_cognate_classes_pred_perDataPoint.pkl","wb"))



pickle.dump(concepts2embeddings,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/concepts2embeddings.pkl","wb"))
pickle.dump(concepts2y_pred,codecs.open("pickled_stuff/pipeline_trainOnEachConcept_ObUgrian/concepts2y_pred.pkl","wb"))
