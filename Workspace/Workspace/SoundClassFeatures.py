from pipeline import *
#from lingpy.sequence import sound_classes as sc
from lingpy import *
class SoundClassFeatures(object):
    def __init__(self,model_name):
        assert model_name =="sca" or model_name =="dolgo" or model_name=="asjp"
        self.model_name = model_name
        self.n_classes = len(set(rc(self.model_name).converter.values()))
        self.id2class = dict((id,c) for id,c in enumerate(set(rc(self.model_name).converter.values())))
        self.class2id = dict((c,id) for id,c in enumerate(set(rc(self.model_name).converter.values())))
        self.oneHots = np.zeros((self.n_classes,self.n_classes),dtype=np.bool)
        for i in self.id2class:
            self.oneHots[i,i] = True
    def encodeWordToClasses(self,word):
        return tokens2class(ipa2tokens(word),self.model_name)
    def encodeWordToOneHots(self,word,padToMaxLength):
        wordMatrix = np.array([self.oneHots[self.class2id[c]]for c in self.encodeWordToClasses(word)])
        if padToMaxLength:
            wordMatrix = wordMatrix[:padToMaxLength]
            return np.pad(np.array(wordMatrix),((0,padToMaxLength - len(wordMatrix)),(0,0)),mode="constant")
        return wordMatrix
