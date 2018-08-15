# Magnet Loss and RepMet in PyTorch

This takes a lot from the Tensorflow Magnet Loss code: [pumpikano/tf-magnet-loss](https://github.com/pumpikano/tf-magnet-loss)

### Magnet Loss
![Figure 3 from paper](magnet.png)

"[Metric Learning with Adaptive Density Discrimination](http://arxiv.org/pdf/1511.05939v2.pdf)" introduced
a new optimization objective for distance metric learning called Magnet Loss that, unlike related losses,
operates on entire neighborhoods in the representation space and adaptively defines the similarity that is
being optimized to account for the changing representations of the training data.

### RepMet
![Figure 2 from paper](repmet.png)

"[RepMet: Representative-based Metric Learning for Classification and One-shot Object Detection](https://arxiv.org/pdf/1806.04728.pdf)"
extends upon magnet loss by storing the centroid as representations that are learnable, rather than just
 statically calculated every now and again with k-means.

## Implementation

Tested with python 3.6 + pytorch 0.4 + cuda 9.1

See `train.py` for training the model, please ensure your `path` is set in `configs.py`.

Currently works on MNIST, working on getting the implementation to work with [Oxford Flowers 102](http://www.robots.ox.ac.uk/~vgg/data/flowers/102/) and [Stanford Dogs](http://vision.stanford.edu/aditya86/ImageNetDogs/) at the moment.

## Evaluation
During training a number of accuracies are calculated:

**1. Batch Accuracy:**
In the batch what % of the batch samples are correctly assigned to their cluster (for magnet loss this is how close to their in-batch mean).

**2. Simple Accuracy:** 
Assign a sample x to its closest training cluster. 
![eq simple](https://latex.codecogs.com/gif.latex?C%28x%29%20%3D%20C%28%5Ctextup%7Barg%7D%20%5Cunderset%7Bi%3D1%2C...%2Cn%5C_clusters%7D%7B%5Ctextup%7Bmin%7D%7D%20%5Cleft%20%5C%7C%20x%20-%20r_i%20%5Cright%20%5C%7C%5E2_2%29)
 
**3. Magnet Accuracy:** 
Use eq. 6 from [Magnet Loss Paper](http://arxiv.org/pdf/1511.05939v2.pdf). Take **L** (or min(L,n_clusters)) closest clusters to a sample x,
then take the sum of the distances of the same classes for each class and take the min (or max after exp).

![eq 6 ML](https://latex.codecogs.com/gif.latex?C%28x%29%20%3D%20%5Ctextup%7Barg%7D%20%5Cunderset%7Bc%3D1%2C...%2CN%7D%7B%5Ctextup%7Bmax%7D%7D%20%5Cfrac%7B%5Csum_%7Bl%3AC%28r_l%29%3Dc%7D%20e%5E%7B-%5Cfrac%7B1%7D%7B2%5Csigma%20%5E2%7D%20%5Cleft%20%5C%7C%20x%20-%20r_l%20%5Cright%20%5C%7C%5E2_2%7D%7D%7B%5Csum_%7Bl%3D1%7D%5E%7BL%7De%5E%7B-%5Cfrac%7B1%7D%7B2%5Csigma%20%5E2%7D%20%5Cleft%20%5C%7C%20x%20-%20r_l%20%5Cright%20%5C%7C%5E2_2%7D%7D)

where ![sig2](https://latex.codecogs.com/gif.latex?%5Csigma%20%5E2) is the avg of all ![sig2](https://latex.codecogs.com/gif.latex?%5Csigma%20%5E2) in training.

**4. RepMet Accuracy:** 
Use eq. 6 from [RepMet Loss Paper](https://arxiv.org/pdf/1806.04728.pdf). Equivalent to Magnet Accuracy however takes all clusters (n_clusters) into consideration not just top **L**.
Also doesn't normalise into probability distribution before the arg max.

![eq 6 RM](https://latex.codecogs.com/gif.latex?C%28x%29%20%3D%20%5Ctextup%7Barg%7D%20%5Cunderset%7Bc%3D1%2C...%2CN%7D%7B%5Ctextup%7Bmax%7D%7D%20%5Csum_%7Bi%3AC%28r_i%29%3Dc%7D%20e%5E%7B-%5Cfrac%7B1%7D%7B2%5Csigma%20%5E2%7D%20%5Cleft%20%5C%7C%20x%20-%20r_i%20%5Cright%20%5C%7C%5E2_2%7D)

where ![sig2](https://latex.codecogs.com/gif.latex?%5Csigma%20%5E2) is set to 0.5 as in training.

**5. Unsupervised Accuracy:** 
Run K-Means on set (ie. don't use trained clusters) and then greedily assign classes to clusters based on the class of samples that fall in that cluster.  

*Test Error can be considered 1-a (1 minus these accuracies)*