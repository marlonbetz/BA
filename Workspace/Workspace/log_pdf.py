from keras.layers import Dense,Reshape,Input,Lambda
from keras.models import Model
from tensorflow.contrib.distributions import MultivariateNormalFull
import numpy as np 

batch_size = 2
n_data = 10
X = np.random.normal(0,1,(n_data,2))
y = np.random.beta(1,1,(n_data,2))

input = Input((2,))
hidden = Dense(100,activation="relu")(input)
mu_pred = Dense(2,activation="linear")(hidden)
sigma_pred = Dense(4,activation="linear")(hidden)
sigma_pred  =Reshape((2,2))(sigma_pred)


mvn = MultivariateNormalFull(mu=mu_pred,sigma=sigma_pred)
def sample_multivariateNormal(args):
    return mvn.sample(sample_shape=(batch_size,2), seed=1337, 
                      name="sample_multivariateNormal")
    
y_pred = Lambda(sample_multivariateNormal, output_shape=(2,),name="y_pred")([mu_pred,sigma_pred])


model = Model(input,y_pred)

def custom_loss(y_true,y_predicted):
    return mvn.log_pdf(value=y_true, name="log_pdf")
    
model.compile("Adam",loss= custom_loss)
print(model.predict(X))
print(model.evaluate(X,y),batch_size=batch_size)