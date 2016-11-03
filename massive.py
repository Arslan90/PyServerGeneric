import networkx as nx
import random
import sys
import os
import math
import subprocess
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt
import getopt
import multiprocessing  # the module we will be using for multiprocessing
##############################################################################
def worker(param):
##############################################################################
    """
    Multiprocessing work
    """
    print param
    os.system(param)
########################################################################################
def main(argv):
    CommandLines=[]
    for i in range(1, 41):
        tmp_dir = 'prog'+ str(i)
        print ("tmp_dir: %r"%tmp_dir)
        CommandLines.append(' /usr/local/packages/matlab2013b/bin/matlab -nodesktop -nodisplay -nojvm -r '+tmp_dir)
        tmp_dir=""
    number_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(number_processes)
    results = pool.map_async(worker, CommandLines)
    pool.close()
    pool.join()
if __name__ == "__main__":
    sys.exit(main(sys.argv))