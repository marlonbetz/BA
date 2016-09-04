import regex 
import numpy as np
class BinaryPhonemeFeatures(object):
    def __init__(self):
        

        self.phonemes = ["p","b","f","v","m","8","4","t","d","s","z","c","n","S","Z","C","j","T","5","k","g","x","N","q","G","X","7","h","l","L","w","y","r","!","V"]
        
        self.binary_features = [
        [False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False],
        [True,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False],
        [False,True,True,False,False,False,False,False,False,True,False,False,False,False,False,False],
        [True,True,True,False,False,False,False,False,False,True,False,False,False,False,False,False],
        [True,True,False,False,False,False,False,False,False,False,False,True,False,False,False,False],
        [True,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False],
        [True,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False],
        [False,False,False,True,False,False,False,False,True,False,False,False,False,False,False,False],
        [True,False,False,True,False,False,False,False,True,False,False,False,False,False,False,False],
        [False,False,False,True,False,False,False,False,False,True,False,False,False,False,False,False],
        [True,False,False,True,False,False,False,False,False,True,False,False,False,False,False,False],
        [True,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False],
        [True,False,False,True,False,False,False,False,False,False,False,True,False,False,False,False],
        [False,False,False,False,True,False,False,False,False,True,False,False,False,False,False,False],
        [True,False,False,False,True,False,False,False,False,True,False,False,False,False,False,False],
        [False,False,False,False,True,False,False,False,False,False,True,False,False,False,False,False],
        [True,False,False,False,True,False,False,False,False,False,True,False,False,False,False,False],
        [True,False,False,False,True,False,False,False,True,False,False,False,False,False,False,False],
        [False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False],
        [False,False,False,False,False,True,False,False,True,False,False,False,False,False,False,False],
        [True,False,False,False,False,True,False,False,True,False,False,False,False,False,False,False],
        [True,False,False,False,False,True,False,False,False,True,False,False,False,False,False,False],
        [True,False,False,False,False,True,False,False,False,False,False,True,False,False,False,False],
        [False,False,False,False,False,False,True,False,True,False,False,False,False,False,False,False],
        [True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,False],
        [True,False,False,False,False,False,True,False,False,True,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False],
        [True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,False],
        [True,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False],
        [True,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False],
        [True,True,False,False,False,True,False,False,False,False,False,False,False,True,False,False],
        [True,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False],
        [True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True],
        [True,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False],
        [True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        ]
        
        self.labels = "voiced Labial Dental Alveolar Palatal/Post-alveolar Velar Uvular Glottal Stop Fricative Affricate Nasal Click Approximant Lateral Rhotic".lower().split()
        self.label_id = dict((label,id) for id,label in enumerate(self.labels)) 
        self.id_label = dict((id,label) for id,label in enumerate(self.labels)) 
        self.phoneme_feature_dict = dict((phoneme,features) 
                                for phoneme,features in zip(self.phonemes,self.binary_features))
        self.feature_phoneme_dict = dict((tuple(features),phoneme) 
                            for phoneme,features in zip(self.phonemes,self.binary_features))
    def encodeWord(self,word,padToMaxLength=None):

        #turn every vowel into generic "V"
        v = "[aeiouE3]"
        word = regex.sub(v,"V",word)
        phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!V"
        phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
        phonemes = regex.findall(phonemeSearchRegex, word)
        wordMatrix = []
        for phoneme in phonemes:
            #if phoneme not in model, get single chars as phonemes instead
            if phoneme not in self.phoneme_feature_dict:
                for ph in regex.findall("["+phonemes_alone+"]", phoneme):
                    wordMatrix.append(self.phoneme_feature_dict[ph])
            else:       
                wordMatrix.append(self.phoneme_feature_dict[phoneme])    
        if padToMaxLength:
            wordMatrix = wordMatrix[:padToMaxLength]
            return np.pad(np.array(wordMatrix),((0,padToMaxLength - len(wordMatrix)),(0,0)),mode="constant")
        return wordMatrix
    def hasFeature(self,phoneme,feature):
        if phoneme not in self.phoneme_feature_dict:
            return False

        return self.phoneme_feature_dict[phoneme][self.label_id[feature]]
    def getString(self,word):
         #turn every vowel into generic "V"
        v = "[aeiouE3]"
        word = regex.sub(v,"V",word)
        phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!V"
        phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
        phonemes = regex.findall(phonemeSearchRegex, word)
        word_new = ""
        for phoneme in phonemes:
            #if phoneme not in model, get single chars as phonemes instead
            if phoneme not in self.phoneme_feature_dict:
                for ph in regex.findall("["+phonemes_alone+"]", phoneme):
                    word_new += ph
            else:       
                word_new += phoneme   
        return word_new
    def decodeWord(self,feature_seq):
        feature_seq = np.array(feature_seq)
        d = np.zeros(feature_seq.shape)
        d.fill(0.5)
        feature_seq = np.greater_equal(feature_seq,d)
        s = ""
        for feature in feature_seq:
            feature = tuple(feature)
            if True not in feature:
                s += ""
            elif feature not in self.feature_phoneme_dict:
                s += "?"
            else:
                s += self.feature_phoneme_dict[feature]
        return s
