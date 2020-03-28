import os
import numpy as np
from scipy.sparse import csr_matrix, dia_matrix
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
from .reco_settings import PARAMS_PATH


class MatrixFactorization():
    def __init__(self, K=8, use_biases=True, alpha=0.1, lmbda=0.01, decay=0.1, momentum=0.75,
                 batch_size=50, batch_growth=1.0, max_size=1024,
                 init_method="random", verbose=False):
        if init_method not in ("svd", "random"):
            print("Error: valid init_method arguments are: ['svd', 'random']")
            raise ValueError
        self.K = K
        self.use_biases = use_biases
        self.alpha = alpha
        self.alpha_ = None
        self.lmbda = lmbda
        self.decay = decay
        self.batch_size = batch_size
        self.batch_size_ = None
        self.batch_growth = batch_growth
        self.max_size = max_size
        self.init_method = init_method
        self.momentum = momentum
        self.U = None
        self.V = None
        self.mu = None
        self.user_bias = None
        self.item_bias = None
        self.grad_v = None
        self.is_initialized = False
        self.n_epochs_ = 0
        self.verbose = verbose

    def _initialize_parameters(self, X: csr_matrix):
        n, d = X.shape
        if self.use_biases:
            self.mu = X.data.mean()
        else:
            self.mu = 0
        if self.init_method == "svd":
            R = X.copy()
            if self.use_biases:
                R.data -= R.data.mean()
            u, s, vt = svds(R, k=self.K)
            self.U = u
            self.V = vt.T
        else:
            self.U = np.random.normal(scale=0.1, size=(n, self.K))
            self.V = np.random.normal(scale=0.1, size=(d, self.K))

        self.user_bias = np.zeros(n)
        self.item_bias = np.zeros(d)
        self.is_initialized = True

    def _run_single_epoch(self, X: csr_matrix, batch_size: int, alpha: float):
        n, d = X.shape
        indices = np.random.permutation(np.arange(n))
        for i in range(int(n / batch_size)):
            batch_start = i * batch_size
            batch_end = batch_start + batch_size
            batch_indices = indices[batch_start:batch_end]
            X_batch = X[batch_indices]
            if X_batch.shape[0] == 0:
                continue
            self._gradient_descent(X_batch, batch_indices, alpha=alpha)
        self.n_epochs_ += 1

    def _gradient_descent(self, X: csr_matrix, batch_indices, alpha):
        U = self.U[batch_indices]
        D = csr_matrix(X, dtype=bool)
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

        if self.use_biases:
            with np.errstate(divide='ignore', invalid='ignore'):
                self.user_bias[batch_indices] += alpha * (
                        np.where(user_error_sums == 0, 0, user_error_sums / np.ravel(D.sum(axis=1)))
                        - self.lmbda * user_bias)
                self.item_bias += alpha * (
                        np.where(item_error_sums == 0, 0, item_error_sums / np.ravel(D.sum(axis=0)))
                        - self.lmbda * self.item_bias)

    def _calculate_batch_size(self, n):
        return min(self.batch_size, self.max_size, n)

    def train(self, X: csr_matrix, n_epochs: int):
        n, d = X.shape

        if not isinstance(n_epochs, int):
            print("Invalid type given for parameter n_epochs. Integer object expected.")
            raise TypeError
        elif n_epochs <= 0:
            print("Invalid value given for parameter n_epochs. Positive integer expected.")
            raise ValueError

        if not self.is_initialized:
            self._initialize_parameters(X)

        for i in range(n_epochs):
            if self.batch_size_ is not None:
                batch_size = self.batch_size_
            else:
                batch_size = self._calculate_batch_size(n)
            if self.alpha_ is not None:
                alpha = self.alpha_
            else:
                alpha = self.alpha

            self._run_single_epoch(X, batch_size, alpha)

            self.batch_size_ = min(int(batch_size * self.batch_growth), self.max_size, n)
            self.alpha_ = alpha / (1 + self.decay)

            if self.verbose:
                print("")
                print(f"Epoch #{self.n_epochs_} | batch size: {batch_size}, alpha: {alpha}")
                print("Norms: |  Bu  |  Bi  |  U  |  V  |")
                print("       ", np.round([
                    np.linalg.norm(self.user_bias),
                    np.linalg.norm(self.item_bias),
                    np.linalg.norm(self.U),
                    np.linalg.norm(self.V)
                ], 2))

    def _predict(self, U=None, V=None, user_bias=None, clip=False):
        if U is None:
            U = self.U
        if V is None:
            V = self.V
        if user_bias is None:
            user_bias = self.user_bias
        prediction = np.dot(U, V.T) + self.mu + user_bias.reshape(-1, 1) + self.item_bias
        if clip:
            return np.clip(prediction, 0.5, 5.0)
        else:
            return prediction

    def get_prediction_sample(self, user_index, clip=True):
        return self._predict(U=self.U[user_index], user_bias=self.user_bias[user_index], clip=clip)

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

    def predict_new(self, X: csr_matrix, alpha=0.05, n_iter=20, lmbda=0.5, solve=False, clip=True):
        '''
        Expected shape of X is (1, d).
        '''
        D = csr_matrix(X, dtype=bool)
        count = D.count_nonzero()
        user_bias = np.zeros(1)

        if solve:
            U = 0.5 * normalize(self._solve_for_u(X, user_bias, lmbda))
        else:
            U = np.random.normal(scale=1 / self.K, size=(1, self.K))

        for i in range(n_iter):
            E = X - D.multiply(self._predict(U, self.V, user_bias))
            U += alpha * ((E @ self.V) / count - lmbda * U)
            # user_bias += alpha * (E.data.mean() - lmbda * user_bias)
        if self.verbose:
            print("||U|| =", np.linalg.norm(U))
            # print("Bu =", user_bias)

        return self._predict(U, self.V, user_bias, clip).flatten()

    def save(self, prefix="", compact=False):
        prefix = os.path.join(PARAMS_PATH, prefix)
        state = self.__dict__.copy()
        if compact:
            for key in 'U user_bias grad_v'.split():
                state[key] = None
        np.save(prefix + "_mfstate", state)

    def load(self, prefix=""):
        prefix = os.path.join(PARAMS_PATH, prefix)
        self.__dict__ = np.load(prefix + "_mfstate.npy", allow_pickle=True).item()
