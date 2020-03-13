import os
import numpy as np
from scipy.sparse import csr_matrix, dia_matrix
from scipy.sparse.linalg import svds
from .reco_settings import PARAMS_PATH


class MatrixFactorization():
    def __init__(self, K=8, alpha=0.1, lmbda=0.02, decay=0.1, momentum=0.9, batch_size=None, n_iter=10, init_method="svd", max_size=1024):
        self.K = K
        self.alpha = alpha
        self.lmbda = lmbda
        self.decay = decay
        self.batch_size = batch_size
        self.max_size = max_size
        self.n_iter = n_iter
        self.init_method = init_method
        self.momentum = momentum
        self.U = None
        self.V = None
        self.D = None
        self.mu = None
        self.user_bias = None
        self.item_bias = None
        self.grad_v = None

    def _initialize_parameters(self, X):
        n, d = X.shape
        self.mu = X.data.mean()
        self.D = csr_matrix(X, dtype=bool)

        if self.init_method == "svd":
            R = X.copy()
            R.data -= R.data.mean()
            u, s, vt = svds(R, k=self.K)
            self.U = u * np.sqrt(s) / 2
            self.V = vt.T * np.sqrt(s) / 2
        else:
            self.U = np.random.normal(scale=0.1, size=(n, self.K))
            self.V = np.random.normal(scale=0.1, size=(d, self.K))

        self.user_bias = np.zeros(n)
        self.item_bias = np.zeros(d)

    def _set_batch_size(self, n):
        if self.batch_size is None:
            batch_size = n
        elif self.batch_size == "auto":
            batch_size = n // 20 + 1
            print('Auto-chosen batch size:', batch_size)
        elif self.batch_size == "adaptive":
            if n < 1000:
                print('Data is too small to use adaptive batch; setting it to auto.')
                batch_size = n // 20 + 1,
            else:
                batch_size = n // 120 + 1
        else:
            batch_size = self.batch_size
        return min(min(self.max_size, batch_size), n)

    def train(self, X: csr_matrix):
        n, d = X.shape
        growth_rate = 1.25
        batch_size = self._set_batch_size(n)

        self._initialize_parameters(X)
        indices = list(range(n))

        for i in range(self.n_iter):
            np.random.shuffle(indices)
            alpha = self.alpha / (1 + i * self.decay)

            if self.batch_size == "adaptive":
                batch_size = min(min(int(batch_size * growth_rate), self.max_size), n)

            for j in range(int(n / batch_size)):
                batch_start = j * batch_size
                batch_end = batch_start + batch_size
                batch_indices = indices[batch_start:batch_end]
                batch_X = X[batch_indices]
                if batch_X.shape[0] == 0: continue
                self._gradient_descent(batch_X, batch_indices, alpha=alpha)

    def _gradient_descent(self, X: csr_matrix, batch_indices, alpha):
        U = self.U[batch_indices]
        D = self.D[batch_indices]
        user_bias = self.user_bias[batch_indices]
        E = X - D.multiply(self._predict(U, self.V, user_bias))

        EV = E @ self.V
        EU = E.T @ U
        with np.errstate(divide='ignore', invalid='ignore'):
            EV = np.where(EV == 0, 0, EV / D.sum(axis=1))
            EU = np.where(EU == 0, 0, EU / D.sum(axis=0).T)

        self.U[batch_indices] += alpha * (EV - self.lmbda * U)

        if self.grad_v is None:
            self.grad_v = EU - self.lmbda * self.V
        else:
            self.grad_v = self.momentum * self.grad_v + (1 - self.momentum) * (EU - self.lmbda * self.V)
        self.V += alpha * self.grad_v

        user_error_sums = np.ravel(E.sum(axis=1))
        item_error_sums = np.ravel(E.sum(axis=0))

        with np.errstate(divide='ignore', invalid='ignore'):
            self.user_bias[batch_indices] += alpha * (
                    np.where(user_error_sums == 0, 0, user_error_sums / np.ravel(D.sum(axis=1)))
                    - self.lmbda * user_bias)
            self.item_bias += alpha * (
                    np.where(item_error_sums == 0, 0, item_error_sums / np.ravel(D.sum(axis=0)))
                    - self.lmbda * self.item_bias)

    def _predict(self, U=None, V=None, user_bias=None, clip=False):
        if U is None:
            U = self.U
        if V is None:
            V = self.V
        if user_bias is None:
            user_bias = self.user_bias
        prediction = np.dot(U, V.T) + self.mu + user_bias.reshape(-1, 1) + self.item_bias
        if clip:
            return np.minimum(np.maximum(prediction, 0.5), 5.0)
        else:
            return prediction

    def _solve_for_u(self, X: csr_matrix, user_bias, lmbda):
        '''
        Solves the quadratic equation for U given fixed V
        '''
        d = X.shape[1]
        D = csr_matrix(X, dtype=bool)
        U = (X - D.multiply(self.mu + user_bias + self.item_bias)) @ self.V @ np.linalg.inv(
            self.V.T @ dia_matrix((D.A, 0), shape=(d, d)) @ self.V + lmbda * np.eye(self.K)
        )
        return U

    def predict_new_solve(self, X: csr_matrix, lmbda=0.5, clip=True):
        '''
        predicts a new user's ratings by directly solving the equation.
        expected shape of X is (1, d).
        '''
        user_bias = np.zeros(1)
        U = self._solve_for_u(X, user_bias, lmbda)
        return self._predict(U, self.V, user_bias, clip)

    def predict_new_gd(self, X: csr_matrix, alpha=0.01, n_iter=20, clip=True):
        '''
        predicts a new user's ratings by gradient descent method.
        expected shape of X is (1, d).
        '''
        D = csr_matrix(X, dtype=bool)
        user_bias = np.zeros(1)
        U = np.random.normal(scale=1/self.K, size=(1, self.K))
        for i in range(n_iter):
            E = X - D.multiply(self._predict(U, self.V, user_bias))
            U += alpha * (E @ self.V - self.lmbda * U)
            user_bias += alpha * (E.data.mean() - self.lmbda * user_bias)
        return self._predict(U, self.V, user_bias, clip)

    def predict_new_hybrid(self, X: csr_matrix, alpha=0.01, lmbda=0.5, n_iter=10, clip=True):
        '''
        combines both Solve/GD methods
        '''
        D = csr_matrix(X, dtype=bool)
        user_bias = np.zeros(1)
        U = self._solve_for_u(X, user_bias, lmbda)
        for i in range(n_iter):
            E = X - D.multiply(self._predict(U, self.V, user_bias))
            U += alpha * (E @ self.V - lmbda * U)
            user_bias += alpha * (E.data.mean() - lmbda * user_bias)
        return self._predict(U, self.V, user_bias, clip)

    def save_params(self, prefix=""):
        prefix = os.path.join(PARAMS_PATH, prefix)
        np.savez(prefix + "_params", V=self.V, item_bias=self.item_bias, K=self.K, lmbda=self.lmbda, mu=self.mu)

    def load_params(self, prefix=""):
        prefix = os.path.join(PARAMS_PATH, prefix)
        params = np.load(prefix + "_params.npz")
        for key, val in params.items():
            try:
                val = val.item()
            except ValueError:
                pass
            else:
                if key == 'K':
                    val = int(val)
            self.__dict__[key] = val