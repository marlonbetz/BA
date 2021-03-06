import regex 
import numpy as np
from gensim.models import Word2Vec
import codecs
class PhonemeEmbeddings(object):
    def __init__(self,pathToASJPCorpusFile,ignoreCoarticulations,sg,size,window,negative,hs,min_count):
        self.fit(pathToASJPCorpusFile, ignoreCoarticulations,sg, size, window, negative, hs, min_count)
    def fit(self,pathToASJPCorpusFile,ignoreCoarticulations,sg,size,window,negative,hs,min_count):
         
         
        print("FIT PHONEME EMBEDDING MODEL")
        self.w2v_model = Word2Vec(sentences=self.extractPhonemes(self.collectWords(pathToASJPCorpusFile,ignoreCoarticulations)),
                             sg = sg,
                             size=size,
                             window=window,
                             negative=negative,
                             hs=hs,
                             min_count=1
                             )
    def extractPhonemes(self,words):
        print("EXTRACT ALL PHONEMES AND ADD WORD BOUNDARIES AND GET RID OF EMPTY STRINGS")
        tmp = [["<s>"]+self.getListofASJPPhonemes(word)+["</s>"] for word in words if len(word) > 0]
        print("number of words:",len(tmp))
        print("number of phoneme tokens:",np.sum([len(t)-2 for t in tmp])) # -2 due to boundary symbols
        return tmp
 
    def collectWords(self,pathToASJPCorpusFile,ignoreCoarticulations):
        print("COLLECT WORDS")
        allWords = []
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
                        if ignoreCoarticulations:
                            words_tmp[i] = words_tmp[i].replace("*","")
                            words_tmp[i] = words_tmp[i].replace("\"","")
                            words_tmp[i] = words_tmp[i].replace("~","")
                            words_tmp[i] = words_tmp[i].replace("$","")

        
                    for i_w,word in enumerate(words_tmp):
                        if len(self.getListofASJPPhonemes(word)) > 0:
                            
                                        
                            """
                            for cells with more than one corresponding word, only take first one
                            """
                            if "," in word:
                                word_splitted = word.split(",")
                                if len(self.getListofASJPPhonemes(word_splitted[0])) > 0:
                                    
                                    allWords.append(word_splitted[0])
                                else:
                                    allWords.append(word_splitted[1])
                            else:
                                allWords.append(word)

        return allWords
                            
    def getListofASJPPhonemes(self,word):
        phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
        phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
        return regex.findall(phonemeSearchRegex, word)
    
    def encodeWord(self,word,padToMaxLength = None):
        phonemes_alone="pbmfv84tdszcnSZCjT5kgxNqGX7hlLwyr!ieaouE3"
        phonemeSearchRegex = "["+phonemes_alone+"][\"\*]?(?!["+phonemes_alone+"]~|["+phonemes_alone+"]{2}\$)|["+phonemes_alone+"]{2}?~|["+phonemes_alone+"]{3}?\$"
        phonemes = regex.findall(phonemeSearchRegex, word)
        wordVector = []
        for phoneme in phonemes:
            #if phoneme not in model, get single chars as phonemes instead
            if phoneme not in self.w2v_model:
                for ph in regex.findall("["+phonemes_alone+"]", phoneme):
                    wordVector.append(self.w2v_model[ph])
            else:       
                wordVector.append(self.w2v_model[phoneme])    
        if padToMaxLength:
            wordVector = wordVector[:padToMaxLength]
            return np.pad(np.array(wordVector),((0,padToMaxLength - len(wordVector)),(0,0)),mode="constant")
        return np.array(wordVector)                           