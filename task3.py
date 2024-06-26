# -*- coding: utf-8 -*-
"""task3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kcqX9zcSrxBRttrBpXUp1VXslrva0HSj

# Chapter 3: Dimensionality Reduction with CUR and SVD
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.utils.extmath import randomized_svd
from tqdm.notebook import tqdm
import warnings
warnings.filterwarnings('ignore')

"""### Importing Dataset
https://raw.githubusercontent.com/palles77/DataPreprocessing/main/AP_Colon_Kidney.csv
"""

df = pd.read_csv('https://raw.githubusercontent.com/palles77/DataPreprocessing/main/AP_Colon_Kidney.csv', index_col=0)
df.head(5)

"""#### Cleaning and Transforming Data"""

X, y = df.drop('Tissue', axis=1), df['Tissue']
Xlog = np.log10(X + 1.0) #log expression data is more convenient to work
print(Xlog.shape)
Xlog.head(7)

"""## Single Value Decomposition(SVD)"""

Xlog_centered = Xlog - Xlog.mean(0)
U, Sigma, V = np.linalg.svd(Xlog_centered)

(U.shape, Sigma.shape, V.shape)

"""### Defining Function to perform SVD"""

def perform_SVD(k, data):
    Xlog_centered = data - data.mean(0)
    U, Sigma, Vt = np.linalg.svd(Xlog_centered)
    X_svd = (U @ np.diag(Sigma))[:, :k]
    print(f"Decomposed Dataset Shape: {X_svd.shape}")
    reduced_df = pd.DataFrame(X_svd, columns=[f"Feature_{i}" for i in range(X_svd.shape[1])])
    print(reduced_df.head(7))
    fig, ax = plt.subplots(figsize=(8,6))

    #Calculating for reduction error
    U_k = U[:, :k]
    Sigma_k = np.diag(Sigma[:k])
    Vt_k = Vt[:k, :]
    A_k = U_k @ Sigma_k @ Vt_k
    error_svd = np.linalg.norm(Xlog_centered - A_k, 'fro')
    print(f'SVD Reduction Error: {error_svd}')

    sns.scatterplot(x=X_svd[:, 0], y=X_svd[:, 1], hue=y, ax=ax)
    plt.title('PCA (SVD) matrix low-dimensional representation', fontsize=14)
    plt.xlabel('First component', fontsize=14)
    plt.ylabel('Second component', fontsize=14)
    ax.legend()

    plt.show()

"""#### SVD into 2 columns"""

perform_SVD(2, Xlog)

"""#### SVD into 5 columns"""

perform_SVD(5, Xlog)

"""## CUR Dimensionality Reduction

### Defining Stochastic CUR Class
"""

import numpy as np
import pandas as pd
from sklearn.utils.extmath import randomized_svd

class CUR():
    def __init__(self, k, eps, it=None, truncated=False):
        self.k = k
        self.eps = eps
        self.trunc = truncated
        self.c = k * np.log(k) / eps**2 #expectation number of sampled columns
        self.C, self.U, self.R = None, None, None #matrices of decomposition
        self.pi_col, self.pi_row = None, None #leverage scores of corresponding columns/rows
        self.col_indices = None
        self.row_indices = None

    def column_select(self, A):
        n = A.shape[1]
        A = np.array(A.copy())
        if self.trunc:
            _, _, v_k = randomized_svd(A, self.k) #for very big matrices
        else:
            _, _, vh = np.linalg.svd(A, full_matrices=False)
            v_k = vh[0:self.k, :]

        pi = 1 / self.k * np.sum(v_k**2, axis=0)
        c_index = [np.random.choice(2,
                        p=[1 - min(1, self.c * pi[i]), min(1, self.c * pi[i])]) for i in range(n)
                  ]
        c_index = np.nonzero(c_index)[0]

        C = A[:, c_index]
        return C, c_index, pi

    def run_CUR(self, A):
        A = np.array(A.copy())
        self.C, self.col_indices, self.pi_col = self.column_select(A)
        self.R, self.row_indices, self.pi_row = self.column_select(A.T)
        self.U = np.linalg.pinv(self.C) @ A @ np.linalg.pinv(self.R.T)
        return self.C, self.U, self.R.T

"""### CUR into 2 Columns"""

k = 5
cur = CUR(k, 0.5, truncated=False)
C,U,R = cur.run_CUR(Xlog)
print(C.shape)
A_cur = C @ U @ R
error_cur = np.linalg.norm(Xlog - A_cur, 'fro')
print(f'CUR Reduction Error: {error_cur}')
ids = np.argsort(cur.pi_col)[::-1][:2]

#plot 2 of them
fig, ax = plt.subplots(figsize=(8,6))
x1 = Xlog.iloc[:, ids[0]]
x2 = Xlog.iloc[:, ids[1]]
sns.scatterplot(x=x1, y=x2, hue=y, ax=ax)
plt.title('CUR matrix low-dimensional representation', fontsize=14)
plt.xlabel(x1.name)
plt.ylabel(x2.name)

plt.show()

X_proj = C@np.linalg.pinv(C)@Xlog
fig, ax = plt.subplots(figsize=(8,6))
x1 = X_proj.iloc[:, ids[0]]
x2 = X_proj.iloc[:, ids[1]]
sns.scatterplot(x=np.array(x1), y=np.array(x2), hue=y, ax=ax)
plt.title('CUR matrix low-dimensional representation in projective space', fontsize=14)
plt.xlabel(x1.name)
plt.ylabel(x2.name)

plt.show()

"""# K-means Clustering"""

from sklearn.cluster import KMeans
k_value=range(3,11)

"""#### Performing K-means clustering from the result of CUR Reduction into 2 columns"""

cur = CUR(2, 0.5, truncated=False)
C,U,R = cur.run_CUR(Xlog)
ids = np.argsort(cur.pi_col)[::-1][:2]

for i in k_value:
  k_means=KMeans(n_clusters=i,random_state=42)
  cluster=k_means.fit_predict(C)
  fig, ax = plt.subplots(figsize=(4,2))
  x1 = Xlog.iloc[:, ids[0]]
  x2 = Xlog.iloc[:, ids[1]]
  sns.scatterplot(x=x1, y=x2, ax=ax,hue=cluster, palette='viridis')
  plt.title('CUR matrix low-dimensional representation', fontsize=14)
  plt.xlabel(x1.name)
  plt.ylabel(x2.name)

plt.show()

"""### Finding Optimal K of CUR using Silhoutte Score and Elbow Method"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Assuming df is your DataFrame fully prepared for clustering
df = C  # Let's assume this DataFrame is ready and preprocessed

# Variables to store results
ssd = []  # Sum of squared distances
silhouette_scores = []

# Range of k to try
k_range = range(3, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(df)
    ssd.append(kmeans.inertia_)  # Inertia: Sum of squared distances of samples to their closest cluster center

    # Compute the silhouette score, only if there are more than 1 cluster (silhouette score requires more than one cluster)
    if k > 1:
        sil_score = silhouette_score(df, kmeans.labels_)
        silhouette_scores.append(sil_score)
    else:
        silhouette_scores.append(None)

# Plotting the Elbow Method graph for SSD
plt.figure(figsize=(10, 5))
plt.plot(k_range, ssd, 'bo-')
plt.xlabel('Number of clusters k')
plt.ylabel('Sum of squared distances (SSD)')
plt.title('Elbow Method For Optimal k')
plt.grid(True)
plt.show()

# Plotting the Silhouette Scores
plt.figure(figsize=(10, 5))
plt.plot(k_range, silhouette_scores, 'ro-')
plt.xlabel('Number of clusters k')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Scores For Different k')
plt.grid(True)
plt.show()

# Displaying the silhouette scores for review
for k, score in zip(k_range, silhouette_scores):
    print(f"Silhouette Score for k={k}: {score:.4f}")

"""#### Performing K-means clustering from the result of SVD Reduction into 2 columns"""

Xlog_centered = Xlog - Xlog.mean(0)
U, Sigma, V = np.linalg.svd(Xlog_centered)
X_svd = (U @ np.diag(Sigma))[:, :2]
print(f"Decomposed Dataset Shape: {X_svd.shape}")
reduced_df = pd.DataFrame(X_svd, columns=[f"Feature_{i}" for i in range(X_svd.shape[1])])
print(reduced_df.head(7))
fig, ax = plt.subplots(figsize=(8,6))

sns.scatterplot(x=X_svd[:, 0], y=X_svd[:, 1], hue=y, ax=ax)
plt.title('PCA (SVD) matrix low-dimensional representation', fontsize=14)
plt.xlabel('First component', fontsize=14)
plt.ylabel('Second component', fontsize=14)
ax.legend()

plt.show()

for i in k_value:
    k_means=KMeans(n_clusters=i,random_state=42)
    clusters = k_means.fit_predict(X_svd)
    fig, ax = plt.subplots(figsize=(4, 2))
    sns.scatterplot(x=X_svd[:, 0], y=X_svd[:, 1], hue=clusters, palette='viridis', ax=ax)
    plt.title(f'K-Means Clustering with k={i}', fontsize=14)
    plt.xlabel('First Component', fontsize=14)
    plt.ylabel('Second Component', fontsize=14)
    ax.legend(title='Cluster')
    plt.show()

"""### Finding Optimal K of SVD using Silhoutte Score and Elbow Method"""

# Assuming df is your DataFrame fully prepared for clustering
df = X_svd  # Let's assume this DataFrame is ready and preprocessed

# Variables to store results
ssd = []  # Sum of squared distances
silhouette_scores = []

# Range of k to try
k_range = range(3, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(df)
    ssd.append(kmeans.inertia_)  # Inertia: Sum of squared distances of samples to their closest cluster center

    # Compute the silhouette score, only if there are more than 1 cluster (silhouette score requires more than one cluster)
    if k > 1:
        sil_score = silhouette_score(df, kmeans.labels_)
        silhouette_scores.append(sil_score)
    else:
        silhouette_scores.append(None)

# Plotting the Elbow Method graph for SSD
plt.figure(figsize=(10, 5))
plt.plot(k_range, ssd, 'bo-')
plt.xlabel('Number of clusters k')
plt.ylabel('Sum of squared distances (SSD)')
plt.title('Elbow Method For Optimal k')
plt.grid(True)
plt.show()

# Plotting the Silhouette Scores
plt.figure(figsize=(10, 5))
plt.plot(k_range, silhouette_scores, 'ro-')
plt.xlabel('Number of clusters k')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Scores For Different k')
plt.grid(True)
plt.show()

# Displaying the silhouette scores for review
for k, score in zip(k_range, silhouette_scores):
    print(f"Silhouette Score for k={k}: {score:.4f}")
