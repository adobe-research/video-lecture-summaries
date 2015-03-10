'''
Created on Mar 6, 2015

@author: hijungshin
'''
import sys
import symbol_classifier as sc

if __name__ == "__main__":
    objdir = sys.argv[1]
    outdir = objdir + "symbols_fill"
    sc.pre_process(objdir, outdir)