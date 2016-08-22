

from keras.layers import Input, Dense, Lambda,merge,Convolution2D,Reshape,MaxPooling2D,UpSampling2D
from keras.layers.noise import GaussianNoise
from keras.models import Model
from keras import backend as K, objectives
from keras.regularizers import l2
from keras.models import load_model


class VAE(object):
    def __init__(self,latent_dim,original_dim,intermediate_dim,batch_size,epsilon_std):
        
        self.batch_size = batch_size
        self.original_dim = original_dim
        self.latent_dim = latent_dim
        self.intermediate_dim = intermediate_dim
        
        
        self.epsilon_std = epsilon_std
        #l2_value = 0.01
        
        #encoder concepts
        
        self.input = Input(batch_shape=(self.batch_size, self.original_dim))
        #input_phono_corrupted = GaussianNoise(sigma=0.01)(input_phono)
        self.intermediate = Dense(self.intermediate_dim,activation="relu",name="layer_h")(self.input)
        
        self.z_mean = Dense(latent_dim,name="z_mean")(self.intermediate)
        self.z_log_std = Dense(latent_dim,name="z_log_std")(self.intermediate)
        
        def sampling(args):
            z_mean, z_log_std = args
            epsilon = K.random_normal(shape=(batch_size, latent_dim),
                                      mean=0., std=epsilon_std)
            return z_mean + K.exp(z_log_std) * epsilon
        
        self.z = Lambda(sampling, output_shape=(latent_dim,),name="layer_z")([self.z_mean, self.z_log_std])
        
        #decoder phono
        # we instantiate these layers separately so as to reuse them later
        self.decoding_layer_intermediate = Dense(self.intermediate_dim,activation="relu",name="decoding_layer_intermediate")
        self.decoding_intermediate = self.decoding_layer_intermediate(self.z)
        
        self.decoding_layer_decoded = Dense(self.original_dim,activation="sigmoid",name="decoding_layer_decoded")
        self.decoded = self.decoding_layer_decoded(self.decoding_intermediate)
        
        
        def vae_loss(input,decoded):
            xent_loss = objectives.binary_crossentropy(input,decoded)
        
            kl_loss = - 0.5 * K.mean(1 + self.z_log_std - K.square(self.z_mean) - K.exp(self.z_log_std), axis=-1)
            return (
                     xent_loss
                     + kl_loss
                     )
        
        self.vae = Model([self.input], [self.decoded])
        
        """
        COMPILING MODELS
        """
        print("COMPILING MODEL")
        self.vae.compile(optimizer='Adam', loss=vae_loss)
        self.encoder = Model([self.input], self.z_mean)
        self.z_posterior_sampler = Model([self.input], self.z)

        
    def fit(self,X,nb_epoch):
        """
        FITTING MODELS
        """
        print("FITTING MODEL")
        self.vae.fit(x=[X],
                 y=[X],
              batch_size=self.batch_size, nb_epoch=nb_epoch)
    def embed(self,X):
        return self.encoder.predict(x=[X],batch_size=self.batch_size)
    def sample_z_posterior(self,X):
        return self.z_posterior_sampler.predict(x=[X],batch_size=self.batch_size)
    
    def save_weights(self,pathToWeights):
        self.vae.save_weights(pathToWeights)
        
        
    def load_weights(self,pathToWeights):
        self.vae.load_weights(pathToWeights)
        