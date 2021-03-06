from pipeline import *

def vectorLinspace(start,stop,num=50):
    assert len(start) == len(stop)
    assert num > 0
    return np.array([np.linspace(start[dim],stop[dim],num) for dim in range(len(start))]).transpose()

def loadVAE_ASJP():
    padToMaxLength = 15
    batch_size = 1
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
    
    
    vae.load_weights("saved_weights/ASJP_2000/pipeline_asjp_2000.h5")
    return vae
def trainOnWordList():
    print("LOAD TEST WORDLIST")
    pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"
    
    languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, {906})
    
    print("VECTORIZE TEST WORDS")
    padToMaxLength=15
    bpf = BinaryPhonemeFeatures()
    X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])
    print("shape of X:",X.shape)
    
    print("FIT VAE")
    
    batch_size = X.shape[0]
    dim_phoneme_embeddings = 16
    original_dim = dim_phoneme_embeddings * padToMaxLength
    latent_dim = 20
    intermediate_dim = 500
    
    
    epsilon_std = 0.01
    nb_epoch =4000
    
    vae = VAE(latent_dim=latent_dim,
              original_dim=original_dim,
              intermediate_dim=intermediate_dim,
              batch_size=batch_size,
              epsilon_std=epsilon_std)
    
    vae.fit(X,
          nb_epoch=nb_epoch)
    print("NEW VAE OBJECT FOR SMALLER BATCH SIZE")
    vae.save_weights("weights_tmp.h5")
    vae = VAE(latent_dim=latent_dim,
              original_dim=original_dim,
              intermediate_dim=intermediate_dim,
              batch_size=1,
              epsilon_std=epsilon_std)
    vae.load_weights("weights_tmp.h5")
    return vae

def decodedLinearWalk(word1,word2,num,vae,bpf):
    binary_code1,binary_code2 = bpf.encodeWord(word1, padToMaxLength),bpf.encodeWord(word2, padToMaxLength)
    embedding1,embedding2 = vae.embed(binary_code1.reshape(1,-1)),vae.embed(binary_code2.reshape(1,-1))
    linspace = vectorLinspace(embedding1.flatten(), embedding2.flatten(), num)
    return [bpf.decodeWord(vae.generator.predict(loc.reshape((1,-1))).reshape((padToMaxLength,-1))  ) for loc in linspace]
vae = trainOnWordList()
padToMaxLength  =15
bpf = BinaryPhonemeFeatures()
word = "dy~Ery~Evo"
print(word)
binary_code = bpf.encodeWord(word, padToMaxLength)
embedding = vae.embed(binary_code.reshape(1,-1))
generated = vae.generator.predict(embedding).reshape((padToMaxLength,-1))
decoded = bpf.decodeWord(generated)
print(decoded)
print(decodedLinearWalk("th~ryE", "dy~Ery~Evo", 10, vae, bpf))
print(decodedLinearWalk("arbol", "abr3", 10, vae, bpf))
print(decodedLinearWalk("bi3m", "dy~Ery~Evo", 10, vae, bpf))
print(decodedLinearWalk("dZEvo", "dy~Ery~Evo", 10, vae, bpf))
