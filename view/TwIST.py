#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 18:39:09 2017

@author: vittoriobisin
"""

"""
desampleConvolvedNoise : raw sensor with noise
A : System matrix
    matrix with each row is for each pixel source position 
    [   k(x1,y1), k(x2,y1), ..., k(xn, y1),
        k(x1,y2), k(x2,y2), ..., k(xn, y2),
        .
        .
        k(x1,y3), k(x2,y3), ..., k(xn, y3),]
realSignal = The real signal without noise
tau : regularization parameter
alpha : parametar alpha of TwiIST (optional), ex.22 of the paper
beta : parametar alpha of TwiIST (optional), ex.23 of the paper
"""

import importlib.util
import os
import numpy as np

# def TwIST(desampleConvolvedNoise,A,tau,lamb,realSignal,alpha,beta): # original function head
def TwIST(desampleConvolvedNoise,A,tau,realSignal,alpha,beta):
    import numpy as np
    from TVNorm import TVNorm
    from TV_denoise import TV_denoise
    # TVNorm = TVNorm.TVNorm
    # TV_denoise = TV_denoise.TV_denoise
    import scipy.stats

    
    #stopping criterions
    iter=1
    IST_iters=0
    TwIST_iters=0
    for_ever=2
    maxiter=1000
    tau=1000

    x=np.transpose(np.matrix(np.zeros(1000)))
    xm2=x
    xm1=xm2
    mse=list()
    SNR=list()
    SAD=list()
    mse.append(sum(((np.square(x-realSignal))))/np.float64(len(x)))
    SNR.append(scipy.stats.signaltonoise(x))
    SAD.append(sum(abs(x-realSignal)))    

    
    j=1
    i=1
    max_svd=1 
    resid=desampleConvolvedNoise-A*x
    flattenedResid=np.matrix(resid.flatten())
    prev_f=np.matrix.item(.5*(flattenedResid*np.transpose(flattenedResid))+tau*TVNorm(x))
    
    initialResid=resid
    
## TwIST iteration

    print("i've started")
    while iter < maxiter:
        for_ever=3
        grad=np.transpose(A)*resid
        while for_ever>2:
            j+=1
            
            #Call the shrinkage/denoising function
            x=np.float64(TV_denoise(xm1+grad/max_svd,tau/max_svd))
            
            
            # If not the first TwIST iteration
            if IST_iters>=2 or TwIST_iters>0:
                print("Things are progressing")
                xm2=(alpha-beta)*xm1 +(1-alpha*xm2+beta*x)
                resid=desampleConvolvedNoise-A*xm2
                f=np.matrix.item(.5*(np.transpose(resid.flatten()*np.transpose(resid.flatten()))+tau*TVNorm(x)))
                if f>prev_f:
                    TwIST_iters=0
                else:
                    TwIST_iters=TwIST_iters+1
                    IST_iters=0
                    x=xm2
                    print(i)
                    i+=1
                    for_ever=1
                    break
            #If the first TwIST iteration (procedure of MTwIST)    
            else:
                resid=desampleConvolvedNoise-A*x
                f=np.matrix.item(5*(resid.flatten()*np.transpose(resid.flatten()))+tau*TVNorm(x))

                if f>prev_f:
                    print("f is increasing")
                    max_svd=2*max_svd
                    IST_iters=0
                    TwIST_iters=0   
                else:
                    TwIST_iters=TwIST_iters+1
                    print(i)
                    i+=1
                    for_ever=1
                    break
        xm2=xm1    
        xm1=x
        iter=iter+1
        print(iter)
        prev_f=f        
        mse.append(sum(((np.square(x-realSignal))))/np.float64(len(x)))
        SNR.append(scipy.stats.signaltonoise(x))
        SAD.append(sum(abs(x-realSignal))) 
        
        return x



def clean_out_TwIST(desampleConvolvedNoise, A, tau, realSignal, alpha, beta):
    import numpy as np
    
    # Custom SNR calculation
    def calculate_snr(signal, axis=None):
        mean_signal = np.mean(signal, axis)
        std_signal = np.std(signal, axis)
        return np.where(std_signal == 0, 0, mean_signal / std_signal)
    
    # Ensure A is a numpy array
    A = np.array(A)
    desampleConvolvedNoise = np.array(desampleConvolvedNoise)
    realSignal = np.array(realSignal)

    # Ensure proper shapes
    if desampleConvolvedNoise.ndim == 1:
        desampleConvolvedNoise = desampleConvolvedNoise[:, np.newaxis]
    if realSignal.ndim == 1:
        realSignal = realSignal[:, np.newaxis]
    
    # Check dimensions
    m, n = A.shape
    if desampleConvolvedNoise.shape[0] != m:
        raise ValueError(f"Incompatible shapes: A has {m} rows but desampleConvolvedNoise has {desampleConvolvedNoise.shape[0]} rows")
    if realSignal.shape[0] != n:
        raise ValueError(f"Incompatible shapes: A has {n} columns but realSignal has {realSignal.shape[0]} rows")
    
    # Stopping criteria and initialization
    iter = 1
    maxiter = 1000
    x = np.zeros((n, 1))
    xm2 = x
    xm1 = xm2
    mse = [np.mean((x - realSignal) ** 2)]
    SNR = [calculate_snr(x, axis=None)]
    SAD = [np.sum(np.abs(x - realSignal))]
    
    while iter < maxiter:
        # Compute the gradient
        Ax = np.dot(A, x)
        if Ax.shape != desampleConvolvedNoise.shape:
            raise ValueError(f"Incompatible shapes: np.dot(A, x) has shape {Ax.shape} but desampleConvolvedNoise has shape {desampleConvolvedNoise.shape}")
        grad = np.dot(A.T, (desampleConvolvedNoise - Ax))
        
        # Perform the TV denoising/shrinkage step
        x = TV_denoise(xm1 + grad / 1.0, tau / 1.0)
        
        if iter > 1:
            xm2 = (alpha - beta) * xm1 + (1 - alpha) * xm2 + beta * x
            x = xm2

        # Update previous estimates
        xm2 = xm1
        xm1 = x
        
        # Monitor convergence
        iter += 1
        mse.append(np.mean((x - realSignal) ** 2))
        SNR.append(calculate_snr(x, axis=None))
        SAD.append(np.sum(np.abs(x - realSignal)))

        # Check for convergence
        if iter % 10 == 0:
            print(f"Iteration {iter}: MSE = {mse[-1]}, SNR = {SNR[-1]}, SAD = {SAD[-1]}")
    
    return x



def TwIST2(desampleConvolvedNoise, A, tau, alpha, beta, realSignal):
    import numpy as np
    from TVNorm import TVNorm
    from TV_denoise import TV_denoise

    # Custom SNR calculation
    def calculate_snr(signal, axis=None):
        mean_signal = np.mean(signal, axis)
        std_signal = np.std(signal, axis)
        return np.where(std_signal == 0, 0, mean_signal / std_signal)
    
    # Ensure A is a numpy array
    A = np.array(A)
    desampleConvolvedNoise = np.array(desampleConvolvedNoise)
    realSignal = np.array(realSignal)

    # Ensure proper shapes
    if desampleConvolvedNoise.ndim == 1:
        desampleConvolvedNoise = desampleConvolvedNoise[:, np.newaxis]
    if realSignal.ndim == 1:
        realSignal = realSignal[:, np.newaxis]
    
    # Check dimensions
    m, n = A.shape
    if desampleConvolvedNoise.shape[0] != m:
        raise ValueError(f"Incompatible shapes: A has {m} rows but desampleConvolvedNoise has {desampleConvolvedNoise.shape[0]} rows")
    if realSignal.shape[0] != n:
        raise ValueError(f"Incompatible shapes: A has {n} columns but realSignal has {realSignal.shape[0]} rows")
    
    # Stopping criteria and initialization
    iter = 1
    maxiter = 1000
    x = np.zeros((n, 1))
    xm2 = x
    xm1 = xm2
    mse = [np.mean((x - realSignal) ** 2)]
    SNR = [calculate_snr(x, axis=None)]
    SAD = [np.sum(np.abs(x - realSignal))]
    
    while iter < maxiter:
        # Compute the gradient
        Ax = np.dot(A, x)
        if Ax.shape != desampleConvolvedNoise.shape:
            raise ValueError(f"Incompatible shapes: np.dot(A, x) has shape {Ax.shape} but desampleConvolvedNoise has shape {desampleConvolvedNoise.shape}")
        grad = np.dot(A.T, (desampleConvolvedNoise - Ax))
        
        # Perform the TV denoising/shrinkage step
        x = TV_denoise(xm1 + grad, tau)
        
        if iter > 1:
            xm2 = (alpha - beta) * xm1 + (1 - alpha) * xm2 + beta * x
            x = xm2

        # Update previous estimates
        xm2 = xm1
        xm1 = x
        
        # Monitor convergence
        iter += 1
        mse.append(np.mean((x - realSignal) ** 2))
        SNR.append(calculate_snr(x, axis=None))
        SAD.append(np.sum(np.abs(x - realSignal)))

        # Check for convergence
        if iter % 10 == 0:
            print(f"Iteration {iter}: MSE = {mse[-1]}, SNR = {SNR[-1]}, SAD = {SAD[-1]}")
    
    return x
