import numpy as np
from scipy.stats import multivariate_normal as mvn
from scipy.stats import gaussian_kde

prior_pdf = lambda x: mvn.pdf(x, np.zeros(2), np.identity(2))

posterior_dist = np.random.normal(2,1.5,(1000,2))
posterior_kernel = gaussian_kde(posterior_dist.T)
posterior_pdf = lambda x : posterior_kernel.pdf(x)

X  =np.arange(-4,4,0.1)
Y  =np.arange(-4,4,0.1)

log_prior = np.array([prior_pdf([x,y]) for x in X for y in Y]).reshape(80,80)
log_posterior = np.array([posterior_pdf([x,y]) for x in X for y in Y]).reshape(80,80)

kld = np.exp(log_posterior)* (log_posterior -log_prior)

import matplotlib.pyplot as plt



plt.imshow(kld,alpha=1)
#plt.imshow(log_prior,alpha=0.1)
#plt.imshow(log_posterior,alpha=0.1)
plt.show()