import numpy as np
import math as mt
from scipy.special import factorial

C=10
lam= 2/5.5
mu=1/10

def computeQ(c,l,m):
	arr1=np.reciprocal(factorial(np.arange(c),exact=False))
	arr2=np.power((l/m),np.arange(c))
	U = mt.ceil(np.sum( np.multiply(arr1,arr2)) )
	return U


def main():


if __name__ == '__main__':
	main()