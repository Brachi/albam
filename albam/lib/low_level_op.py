# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 15:56:59 2019

@author: aguevara
"""
# https://brilliant.org/wiki/radix-sort/
import ctypes


def log2_64(value):
    tab64 = [63, 0, 58, 1, 59, 47, 53, 2,
             60, 39, 48, 27, 54, 33, 42, 3,
             61, 51, 37, 40, 49, 18, 28, 20,
             55, 30, 34, 11, 43, 14, 22, 4,
             62, 57, 46, 52, 38, 26, 32, 41,
             50, 36, 17, 19, 29, 10, 13, 21,
             56, 45, 25, 31, 35, 16, 9, 12,
             44, 24, 15, 8, 23, 7, 6, 5,
             ]
    value |= value >> 1
    value |= value >> 2
    value |= value >> 4
    value |= value >> 8
    value |= value >> 16
    value |= value >> 32
    return tab64[ctypes.c_uint64((value - (value >> 1)) * 0x07EDD5E59A4E28C2).value >> 58]


bitmask = [sum([2**j for j in range(i)]) for i in range(0, 64)]


def counting_sort(A, digit, ix):
    # "A" is a list to be sorted, radix is the base of the number system, digit is the digit
    # we want to sort by

    # create a list B which will be the sorted list
    B = [0] * len(A)
    C = [0] * int(1 << ix)
    # counts the number of occurences of each digit in A
    for i in range(0, len(A)):
        digit_of_Ai = (A[i] >> (ix * digit)) & bitmask[ix]
        C[digit_of_Ai] = C[digit_of_Ai] + 1
        # now C[i] is the value of the number of elements in A equal to i

    # this FOR loop changes C to show the cumulative # of digits up to that index of C
    for j in range(1, 1 << ix):
        C[j] = C[j] + C[j - 1]
        # here C is modifed to have the number of elements <= i
    for m in range(len(A) - 1, -1, -1):  # to count down (go through A backwards)
        digit_of_Ai = (A[m] >> (ix * digit)) & bitmask[ix]
        C[digit_of_Ai] = C[digit_of_Ai] - 1
        B[C[digit_of_Ai]] = A[m]

    return B

# alist = [9,3,1,4,5,7,7,2,2]
# print countingSort(alist,0,10)


def radix_sort(A, ix):
    # radix is the base of the number system
    # k is the largest number in the list
    k = max(A)
    # output is the result list we will build
    output = A
    # compute the number of digits needed to represent k
    digits = log2_64(k) // ix + 1
    for i in range(digits):
        output = counting_sort(output, i, ix)
    return output
