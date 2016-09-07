from pipeline import *
from string_distances import *
print("LOAD WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, {730})
print("concepts2words")
concepts2words = dict((concept,[word for i,word in enumerate(words) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))
print("concepts2cognate_classes")
concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))

ars = []
ami = []
h = []
c = []
v = []
for i,concept in enumerate(concepts2words):
    words_tmp = concepts2words[concept]
    y_true = concepts2cognate_classes[concept]
    print(i,"/",len(concepts2cognate_classes))
    
    dists = np.zeros((len(words_tmp),len(words_tmp)))
    #print("calculcating distances")
    for i1,w1 in enumerate(words_tmp):
        #print(w1)
        for i2,w2 in enumerate(words_tmp):
            dists[i1,i2] = - levenshtein(w1, w2)
    
    
    damping_factor = 0.5
    
    affinity = "precomputed"
    ap = AffinityPropagation(damping=damping_factor,
                             #preference=pref
                             affinity=affinity
                             )
    #print("fitting ap")

    y_pred = ap.fit_predict(dists)
    n_cognate_classes = len(set(cognate_classes))
    n_concepts = len(set(global_ids))
    y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)
    #print("calculating measures")
    ars.append(metrics.adjusted_rand_score(y_true, y_pred))
    ami.append(metrics.adjusted_mutual_info_score(y_true, y_pred))
    h.append(metrics.homogeneity_score(y_true, y_pred))
    c.append(metrics.completeness_score(y_true, y_pred))
    v.append(metrics.v_measure_score(y_true, y_pred))

print(np.mean(np.array(ars)))
print(np.mean(np.array(ami)))
print(np.mean(np.array(h)))
print(np.mean(np.array(c)))
print(np.mean(np.array(v)))