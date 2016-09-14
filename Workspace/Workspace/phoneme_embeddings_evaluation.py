import numpy as np

SimilarityTestData = [
                        #check for voiceless plosive > nasal via unvoiced plosive 
                        {"positive":"p n".split(),"negative":"t".split(),"true":"m".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"t m".split(),"negative":"p".split(),"true":"n".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"k n".split(),"negative":"t".split(),"true":"N".split(),"tags":["consonant","plain","apply_nasal"]},
                        #check for voiced plosive > nasal via voiced plosive 
                        {"positive":"b n".split(),"negative":"d".split(),"true":"m".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"d m".split(),"negative":"b".split(),"true":"n".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"g n".split(),"negative":"d".split(),"true":"N".split(),"tags":["consonant","plain","apply_nasal"]},
                        
                        
                        #check for plain voiced plosive >  plain nasal via plain unvoiced plosive 
                        {"positive":"b n".split(),"negative":"t".split(),"true":"m".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"d m".split(),"negative":"p".split(),"true":"n".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"g n".split(),"negative":"t".split(),"true":"N".split(),"tags":["consonant","plain","apply_nasal"]},
                        
                        #check plain unvoiced plosive > plain voiced plosive via plain voiced plosive
                        {"positive":"p d".split(),"negative":"t".split(),"true":"b".split(),"tags":["consonant","apply_voice","plain","plosive"]},
                        {"positive":"t b".split(),"negative":"p".split(),"true":"d".split(),"tags":["consonant","apply_voice","plain","plosive"]},
                        {"positive":"k d".split(),"negative":"t".split(),"true":"g".split(),"tags":["consonant","apply_voice","plain","plosive"]},
                        
                        #check plain voiced plosive > plain unvoiced plosive via plain unvoiced plosive                    
                        {"positive":"b t".split(),"negative":"d".split(),"true":"p".split(),"tags":["consonant","remove_voice","plain","plosive"]},
                        {"positive":"d p".split(),"negative":"b".split(),"true":"t".split(),"tags":["consonant","remove_voice","plain","plosive"]},
                        {"positive":"g t".split(),"negative":"d".split(),"true":"k".split(),"tags":["consonant","remove_voice","plain","plosive"]},
                        
                        #check for labialized voiced plosive >  labialized nasal via labialized unvoiced plosive 
                        {"positive":"bw~ nw~".split(),"negative":"tw~".split(),"true":"mw~".split(),"tags":["consonant","labialized","complex"]},
                        {"positive":"dw~ mw~".split(),"negative":"pw~".split(),"true":"nw~".split(),"tags":["consonant","labialized","complex"]},
                        {"positive":"gw~ nw~".split(),"negative":"tw~".split(),"true":"Nw~".split(),"tags":["consonant","labialized","complex"]},
                        
                        #check labialized unvoiced plosive > labialized voiced plosive via labialized voiced plosive
                        {"positive":"pw~ dw~".split(),"negative":"tw~".split(),"true":"bw~".split(),"tags":["consonant","apply_voice","labialized","plosive","complex"]},
                        {"positive":"tw~ bw~".split(),"negative":"pw~".split(),"true":"dw~".split(),"tags":["consonant","apply_voice","labialized","plosive","complex"]},
                        {"positive":"kw~ dw~".split(),"negative":"tw~".split(),"true":"gw~".split(),"tags":["consonant","apply_voice","labialized","plosive","complex"]},
                        
                        #check labialized voiced plosive > labialized unvoiced plosive via labialized unvoiced plosive                    
                        {"positive":"bw~ tw~".split(),"negative":"dw~".split(),"true":"pw~".split(),"tags":["consonant","remove_voice","labialized","plosive","complex"]},
                        {"positive":"dw~ pw~".split(),"negative":"bw~".split(),"true":"tw~".split(),"tags":["consonant","remove_voice","labialized","plosive","complex"]},
                        {"positive":"gw~ tw~".split(),"negative":"dw~".split(),"true":"kw~".split(),"tags":["consonant","remove_voice","labialized","plosive","complex"]},
                        
                        
                        
                        #check for palazalized voiced plosive >  palazalized nasal via palazalized unvoiced plosive 
                        {"positive":"by~ ny~".split(),"negative":"ty~".split(),"true":"my~".split(),"tags":["consonant","palatalized","apply_nasal","complex"]},
                        {"positive":"dy~ my~".split(),"negative":"py~".split(),"true":"ny~".split(),"tags":["consonant","palatalized","apply_nasal","complex"]},
                        {"positive":"gy~ ny~".split(),"negative":"ty~".split(),"true":"Ny~".split(),"tags":["consonant","palatalized","apply_nasal","complex"]},
                        
                        #check palazalized unvoiced plosive > palazalized voiced plosive via palazalized voiced plosive
                        {"positive":"py~ dy~".split(),"negative":"ty~".split(),"true":"by~".split(),"tags":["consonant","apply_voice","palatalized","plosive","complex"]},
                        {"positive":"ty~ by~".split(),"negative":"py~".split(),"true":"dy~".split(),"tags":["consonant","apply_voice","palatalized","plosive","complex"]},
                        {"positive":"ky~ dy~".split(),"negative":"ty~".split(),"true":"gy~".split(),"tags":["consonant","apply_voice","palatalized","plosive","complex"]},
                        
                        #check palazalized voiced plosive > palazalized unvoiced plosive via palazalized unvoiced plosive                    
                        {"positive":"by~ ty~".split(),"negative":"dy~".split(),"true":"py~".split(),"tags":["consonant","remove_voice","palatalized","plosive","complex"]},
                        {"positive":"dy~ py~".split(),"negative":"by~".split(),"true":"ty~".split(),"tags":["consonant","remove_voice","palatalized","plosive","complex"]},
                        {"positive":"gy~ ty~".split(),"negative":"dy~".split(),"true":"ky~".split(),"tags":["consonant","remove_voice","palatalized","plosive","complex"]},
                        
                                                
                                                
                        #check for aspirated voiced plosive >  aspirated nasal via aspirated unvoiced plosive 
                        {"positive":"bh~ nh~".split(),"negative":"th~".split(),"true":"mh~".split(),"tags":["consonant","aspirated","apply_nasal","complex"]},
                        {"positive":"dh~ mh~".split(),"negative":"ph~".split(),"true":"nh~".split(),"tags":["consonant","aspirated","apply_nasal","complex"]},
                        {"positive":"gh~ nh~".split(),"negative":"th~".split(),"true":"Nh~".split(),"tags":["consonant","aspirated","apply_nasal","complex"]},
                        
                        #check aspirated unvoiced plosive > aspirated voiced plosive via aspirated voiced plosive
                        {"positive":"ph~ dh~".split(),"negative":"th~".split(),"true":"bh~".split(),"tags":["consonant","apply_voice","aspirated","plosive","complex"]},
                        {"positive":"th~ bh~".split(),"negative":"ph~".split(),"true":"dh~".split(),"tags":["consonant","apply_voice","aspirated","plosive","complex"]},
                        {"positive":"kh~ dh~".split(),"negative":"th~".split(),"true":"gh~".split(),"tags":["consonant","apply_voice","aspirated","plosive","complex"]},
                        
                        #check aspirated voiced plosive > aspirated unvoiced plosive via aspirated unvoiced plosive                    
                        {"positive":"bh~ th~".split(),"negative":"dh~".split(),"true":"ph~".split(),"tags":["consonant","remove_voice","aspirated","plosive","complex"]},
                        {"positive":"dh~ ph~".split(),"negative":"bh~".split(),"true":"th~".split(),"tags":["consonant","remove_voice","aspirated","plosive","complex"]},
                        {"positive":"gh~ th~".split(),"negative":"dh~".split(),"true":"kh~".split(),"tags":["consonant","remove_voice","aspirated","plosive","complex"]},
                        
                        
                        #check for glottalized voiced plosive >  glottalized nasal via glottalized unvoiced plosive 
                        {"positive":"b\" n\"".split(),"negative":"t\"".split(),"true":"m\"".split(),"tags":["consonant","glottalized","apply_nasal"]},
                        {"positive":"d\" m\"".split(),"negative":"p\"".split(),"true":"n\"".split(),"tags":["consonant","glottalized","apply_nasal"]},
                        {"positive":"g\" n\"".split(),"negative":"t\"".split(),"true":"N\"".split(),"tags":["consonant","glottalized","apply_nasal"]},
                        
                        #check glottalized unvoiced plosive > glottalized voiced plosive via glottalized voiced plosive
                        {"positive":"p\" d\"".split(),"negative":"t\"".split(),"true":"b\"".split(),"tags":["consonant","apply_voice","glottalized","plosive"]},
                        {"positive":"t\" b\"".split(),"negative":"p\"".split(),"true":"d\"".split(),"tags":["consonant","apply_voice","glottalized","plosive"]},
                        {"positive":"k\" d\"".split(),"negative":"t\"".split(),"true":"g\"".split(),"tags":["consonant","apply_voice","glottalized","plosive"]},
                        
                        #check glottalized voiced plosive > glottalized unvoiced plosive via glottalized unvoiced plosive                    
                        {"positive":"b\" t\"".split(),"negative":"d\"".split(),"true":"p\"".split(),"tags":["consonant","remove_voice","glottalized","plosive"]},
                        {"positive":"d\" p\"".split(),"negative":"b\"".split(),"true":"t\"".split(),"tags":["consonant","remove_voice","glottalized","plosive"]},
                        {"positive":"g\" t\"".split(),"negative":"d\"".split(),"true":"k\"".split(),"tags":["consonant","remove_voice","glottalized","plosive"]},
                        
                        
                        
                        
                        
                        #check unvoiced pulmonic plosive  > unvoiced aspirated plosive via unvoiced aspirated plosive                    
                        {"positive":"p th~".split(),"negative":"t".split(),"true":"ph~".split(),"tags":["consonant","aspirated","plosive"]},
                        {"positive":"t ph~".split(),"negative":"p".split(),"true":"th~".split(),"tags":["consonant","aspirated","plosive"]},
                        {"positive":"k th~".split(),"negative":"t".split(),"true":"kh~".split(),"tags":["consonant","aspirated","plosive"]},
                        
                        #check voiced pulmonic plosive  > voiced aspirated plosive via voiced aspirated plosive                    
                        {"positive":"b dh~".split(),"negative":"d".split(),"true":"bh~".split(),"tags":["consonant","aspirated","plosive"]},
                        {"positive":"d bh~".split(),"negative":"b".split(),"true":"dh~".split(),"tags":["consonant","aspirated","plosive"]},
                        {"positive":"g dh~".split(),"negative":"d".split(),"true":"gh~".split(),"tags":["consonant","aspirated","plosive"]},
                        
                        
                        #check unvoiced plain plosive  > unvoiced palatalized plosive via unvoiced palatalized plosive                    
                        {"positive":"p ty~".split(),"negative":"t".split(),"true":"py~".split(),"tags":["consonant","palatalized","plosive"]},
                        {"positive":"t py~".split(),"negative":"p".split(),"true":"ty~".split(),"tags":["consonant","palatalized","plosive"]},
                        {"positive":"k ty~".split(),"negative":"t".split(),"true":"ky~".split(),"tags":["consonant","palatalized","plosive"]},
                        
                        #check voiced plain plosive  > voiced palatalized plosive via voiced palatalized plosive                    
                        {"positive":"b dy~".split(),"negative":"d".split(),"true":"by~".split(),"tags":["consonant","palatalized","plosive"]},
                        {"positive":"d by~".split(),"negative":"b".split(),"true":"dy~".split(),"tags":["consonant","palatalized","plosive"]},
                        {"positive":"g dy~".split(),"negative":"d".split(),"true":"gy~".split(),"tags":["consonant","palatalized","plosive"]},
                        
                        #check unvoiced plain plosive  > unvoiced labialized plosive via unvoiced labialized plosive                    
                        {"positive":"p t\"".split(),"negative":"t".split(),"true":"p\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"t p\"".split(),"negative":"p".split(),"true":"t\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"k t\"".split(),"negative":"t".split(),"true":"k\"".split(),"tags":["consonant","glottalized","plosive"]},
                        
                        #check voiced plain plosive  > voiced labialized plosive via voiced labialized plosive                    
                        {"positive":"b d\"".split(),"negative":"d".split(),"true":"b\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"d b\"".split(),"negative":"b".split(),"true":"d\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"g d\"".split(),"negative":"d".split(),"true":"g\"".split(),"tags":["consonant","glottalized","plosive"]},
                        
                        #check unvoiced pulmonic plosive  > unvoiced glottalized plosive via unvoiced glottalized plosive                    
                        {"positive":"p t\"".split(),"negative":"t".split(),"true":"p\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"t p\"".split(),"negative":"p".split(),"true":"t\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"k t\"".split(),"negative":"t".split(),"true":"k\"".split(),"tags":["consonant","glottalized","plosive"]},
                        
                        #check voiced pulmonic plosive  > voiced glottalized plosive via voiced glottalized plosive                    
                        {"positive":"b d\"".split(),"negative":"d".split(),"true":"b\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"d b\"".split(),"negative":"b".split(),"true":"d\"".split(),"tags":["consonant","glottalized","plosive"]},
                        {"positive":"g d\"".split(),"negative":"d".split(),"true":"g\"".split(),"tags":["consonant","glottalized","plosive"]},
                        
                        
                        #check POA transitions for unvoiced plosives
                        {"positive":"p d".split(),"negative":"b".split(),"true":"t".split(),"tags":["consonant","plain","plosive"]},
                        {"positive":"t b".split(),"negative":"d".split(),"true":"p".split(),"tags":["consonant","plain","plosive"]},
                        {"positive":"k d".split(),"negative":"g".split(),"true":"t".split(),"tags":["consonant","plain","plosive"]},  
                        
                        #check POA transitions for voiced plosives
                        {"positive":"b t".split(),"negative":"p".split(),"true":"d".split(),"tags":["consonant","plain","plosive"]},
                        {"positive":"d p".split(),"negative":"t".split(),"true":"b".split(),"tags":["consonant","plain","plosive"]},
                        {"positive":"g t".split(),"negative":"k".split(),"true":"d".split(),"tags":["consonant","plain","plosive"]},   
                        
                        #check POA transitions for nasals
                        {"positive":"m d".split(),"negative":"b".split(),"true":"n".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"n b".split(),"negative":"d".split(),"true":"m".split(),"tags":["consonant","plain","apply_nasal"]},
                        {"positive":"N d".split(),"negative":"g".split(),"true":"n".split(),"tags":["consonant","plain","apply_nasal"]},
                        
                        ##FRICATIVES  
                        
                        #check POA transitions for unvoiced fricatives 
                        {"positive":"f t".split(),"negative":"p".split(),"true":"s".split(),"tags":["consonant","fricative","plain"]},
                        {"positive":"s p".split(),"negative":"t".split(),"true":"f".split(),"tags":["consonant","fricative","plain"]},
                        {"positive":"x t".split(),"negative":"k".split(),"true":"s".split(),"tags":["consonant","fricative","plain"]},                     
                        {"positive":"X k".split(),"negative":"q".split(),"true":"x".split(),"tags":["consonant","fricative","plain"]},  
                        
                        #check POA transitions for voiced fricatives 
                        {"positive":"v d".split(),"negative":"b".split(),"true":"z".split(),"tags":["consonant","fricative","plain"]},
                        {"positive":"z b".split(),"negative":"d".split(),"true":"v".split(),"tags":["consonant","fricative","plain"]},
                        
                        
                        ###################
                        #vowels
                        
                        #check for roundedness
                        {"positive":"i o".split(),"negative":"e".split(),"true":"u".split(),"tags":["vowel","rounded"]},
                        {"positive":"e u".split(),"negative":"i".split(),"true":"o".split(),"tags":["vowel","rounded"]},
                        
                        #check for height
                        {"positive":"i o".split(),"negative":"u".split(),"true":"e".split(),"tags":["vowel","height"]},
                        {"positive":"e u".split(),"negative":"o".split(),"true":"i".split(),"tags":["vowel","height"]},
                        
                        #check for +nasality 
                        {"positive":"i u*".split(),"negative":"u".split(),"true":"i*".split(),"tags":["vowel","apply_nasalized"]},
                        {"positive":"e o*".split(),"negative":"o".split(),"true":"e*".split(),"tags":["vowel","apply_nasalized"]},
                        {"positive":"u i*".split(),"negative":"i".split(),"true":"u*".split(),"tags":["vowel","apply_nasalized"]},
                        {"positive":"o e*".split(),"negative":"e".split(),"true":"o*".split(),"tags":["vowel","apply_nasalized"]},                       
                        {"positive":"a o*".split(),"negative":"o".split(),"true":"a*".split(),"tags":["vowel","apply_nasalized"]},
                        {"positive":"E e*".split(),"negative":"e".split(),"true":"E*".split(),"tags":["vowel","apply_nasalized"]},
                        {"positive":"3 E*".split(),"negative":"E".split(),"true":"3*".split(),"tags":["vowel","apply_nasalized"]},
                        
                        #check for -nasality 
                        {"positive":"i* u".split(),"negative":"u*".split(),"true":"i".split(),"tags":["vowel","remove_nasalized"]},
                        {"positive":"e* o".split(),"negative":"o*".split(),"true":"e".split(),"tags":["vowel","remove_nasalized"]},
                        {"positive":"u* i".split(),"negative":"i*".split(),"true":"u".split(),"tags":["vowel","remove_nasalized"]},
                        {"positive":"o* e".split(),"negative":"e*".split(),"true":"o".split(),"tags":["vowel","remove_nasalized"]},                       
                        {"positive":"a* o".split(),"negative":"o*".split(),"true":"a".split(),"tags":["vowel","remove_nasalized"]},
                        {"positive":"E* e".split(),"negative":"e*".split(),"true":"E".split(),"tags":["vowel","remove_nasalized"]},
                        {"positive":"3* E".split(),"negative":"E*".split(),"true":"3".split(),"tags":["vowel","remove_nasalized"]},

                        

                      ]
    