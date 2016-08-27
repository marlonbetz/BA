from pipeline import *

print("LOAD TEST WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, {730})

print("VECTORIZE TEST WORDS")
padToMaxLength=15
bpf = BinaryPhonemeFeatures()
X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])
print("shape of X:",X.shape)

latent_dims = [2,5,10,20,50,100,200]
intermediate_dims = [100,200,500]
epsilon_stds = [1,0.1,0.01,0.001]
nb_epochs = [100,500,1000,2000,4000]

ars = np.zeros((len(latent_dims),len(intermediate_dims),len(epsilon_stds),len(nb_epochs)))
ami = np.zeros((len(latent_dims),len(intermediate_dims),len(epsilon_stds),len(nb_epochs)))

n_total = ars.flatten().shape[0]
c = 0
for i_latent_dim,latent_dim in enumerate(latent_dims):
    for i_intermediate_dim,intermediate_dim in enumerate(intermediate_dims):
        for i_epsilon_std,epsilon_std in enumerate(epsilon_stds):
            for i_nb_epoch,nb_epoch in enumerate(nb_epochs):
                print(c,"/",n_total)
                print("FIT VAE")
                
                batch_size = X.shape[0]
                dim_phoneme_embeddings = 16
                original_dim = dim_phoneme_embeddings * padToMaxLength
                
                
                
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
                from scipy.spatial.distance import cosine
                concepts2embeddings = dict((concept,[emb for i,emb in enumerate(embeddings) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))
                concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))
                #for damping_factor in np.arange(0.5,1,0.05):
                damping_factor = 0.5
                
                affinity = "euclidean"
                ap = AffinityPropagation(damping=damping_factor,
                                         #preference=pref
                                         affinity=affinity
                                         )
                
                if affinity == "precomputed":
                    y_pred = ap.fit_predict(np.array([-cosine(u, v) for u in embeddings for v in embeddings]).reshape((len(embeddings),len(embeddings))))
                else:
                    y_pred = ap.fit_predict(embeddings)
                n_cognate_classes = len(set(cognate_classes))
                n_concepts = len(set(global_ids))
                y_true = cognate_classes
                y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)
                ars_tmp = metrics.adjusted_rand_score(y_true, y_pred)
                ami_tmp = metrics.adjusted_mutual_info_score(y_true, y_pred)
                ars[i_latent_dim,i_intermediate_dim,i_epsilon_std,i_nb_epoch] = ars_tmp
                ami[i_latent_dim,i_intermediate_dim,i_epsilon_std,i_nb_epoch] = ami_tmp
                c +=1
print("PICKLING")
import pickle 
pickle.dump(ars,codecs.open("pickled_stuff/pipeline_trainOnConcept_gridSearch/ars.py", "wb"))
pickle.dump(ami,codecs.open("pickled_stuff/pipeline_trainOnConcept_gridSearch/ami.py", "wb"))
