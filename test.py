import numpy as np

# Define a small system matrix A (3x3)
A = np.array([[0.5, 0.2, 0.1],
              [0.1, 0.7, 0.2],
              [0.3, 0.2, 0.8]])

# Define desampleConvolvedNoise (3x1)
desampleConvolvedNoise = np.array([[0.6],
                                   [0.9],
                                   [1.2]])

# Define realSignal (3x1)
realSignal = np.array([[1.0],
                       [1.5],
                       [2.0]])

# Define tau, alpha, beta
tau = 0.1
alpha = 1.0
beta = 0.5


import sys
sys.path.append('gitclone/Image-Restoration-Algorithm-TwIST')

from TwIST import TwIST
x = TwIST(desampleConvolvedNoise, A, tau, realSignal, alpha, beta)
print("Reconstructed signal:", x)


# # Define TVNorm and TV_denoise functions for testing purposes
# def TVNorm(x):
#     return np.sum(np.abs(np.diff(x, axis=0)))

# def TV_denoise(x, tau):
#     return np.sign(x) * np.maximum(np.abs(x) - tau, 0)

# def TwIST(desampleConvolvedNoise, A, tau, realSignal, alpha, beta):
#     import numpy as np
#     def calculate_snr(signal, axis=None):
#         mean_signal = np.mean(signal, axis)
#         std_signal = np.std(signal, axis)
#         return np.where(std_signal == 0, 0, mean_signal / std_signal)
#     A = np.array(A)
#     desampleConvolvedNoise = np.array(desampleConvolvedNoise)
#     realSignal = np.array(realSignal)

#     if desampleConvolvedNoise.ndim == 1:
#         desampleConvolvedNoise = desampleConvolvedNoise[:, np.newaxis]
#     if realSignal.ndim == 1:
#         realSignal = realSignal[:, np.newaxis]
    
#     m, n = A.shape
#     if desampleConvolvedNoise.shape[0] != m:
#         raise ValueError(f"Incompatible shapes: A has {m} rows but desampleConvolvedNoise has {desampleConvolvedNoise.shape[0]} rows")
#     if realSignal.shape[0] != n:
#         raise ValueError(f"Incompatible shapes: A has {n} columns but realSignal has {realSignal.shape[0]} rows")
    
#     # Stopping criteria and initialization
#     iter = 1
#     maxiter = 1000
#     x = np.zeros((n, 1))
#     xm2 = x
#     xm1 = xm2
#     mse = [np.mean((x - realSignal) ** 2)]
#     SNR = [calculate_snr(x, axis=None)]
#     SAD = [np.sum(np.abs(x - realSignal))]
    
#     while iter < maxiter:
#         Ax = np.dot(A, x)
#         if Ax.shape != desampleConvolvedNoise.shape:
#             raise ValueError(f"Incompatible shapes: np.dot(A, x) has shape {Ax.shape} but desampleConvolvedNoise has shape {desampleConvolvedNoise.shape}")
#         grad = np.dot(A.T, (desampleConvolvedNoise - Ax))
#         x = TV_denoise(xm1 + grad / 1.0, tau / 1.0)
        
#         if iter > 1:
#             xm2 = (alpha - beta) * xm1 + (1 - alpha) * xm2 + beta * x
#             x = xm2

#         # Update previous estimates
#         xm2 = xm1
#         xm1 = x
        
#         # Monitor convergence
#         iter += 1
#         mse.append(np.mean((x - realSignal) ** 2))
#         SNR.append(calculate_snr(x, axis=None))
#         SAD.append(np.sum(np.abs(x - realSignal)))

#         # Check for convergence
#         if iter % 10 == 0:
#             print(f"Iteration {iter}: MSE = {mse[-1]}, SNR = {SNR[-1]}, SAD = {SAD[-1]}")
    
#     return x

# x = TwIST(desampleConvolvedNoise, A, tau, realSignal, alpha, beta)
# print("Reconstructed signal:", x)