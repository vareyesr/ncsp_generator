from py_expression_eval import Parser
import random
from sets import Set
import math
import array
import numpy as np
        
class Instance_mult:
    def __init__(self,nb_eq,P,Q,nb_inst,r1,r2,r3,min_dom,max_dom):
        self.nb_eq = nb_eq
        self.P = P 
        self.Q = Q
        self.nb_inst = nb_inst
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.min_dom = min_dom
        self.max_dom = max_dom 
        #create pool
        pool = create_pool(nb_eq,nb_eq,nb_inst)
        #create sets
        
def create_pool(nb_var,unary_eq,nb_inst):
    #create the first n variables
    pool_list = []
    for i in range(0, nb_var):
        pool_list.append('x'+str(i))
    #additional (unary functions)
    for i in range(0,unary_eq):
        pool_list.append(unary_fun()+'('+random_var(pool_list[:nb_var])+')')
    print 'pool list generated for the instance '+str(nb_inst)+':'
    print pool_list
    return pool_list

def unary_fun():        
    unary = ['sin','cos','tan','exp','ln']
    return unary[random.randint(0,len(unary)-1)]

def random_var(poolvar):
    pos = random.randint(0,len(poolvar)-1)
    return poolvar[pos]    
    
def sets_sums(nb_eq):
    print 'falta'
    #create pool of variables    
        
if __name__ == '__main__':
    nseed = input('Enter the seed: ')
    num_instances = input('enter the number of instances to be created: ')
    nb_eq = input('enter the maximum number of variables (minimum set to 3): ')
    max_dom = input('enter maximum domain size: ')
    min_dom = input('enter minimum domain size: ')
    r1 = array.array('i',(i for i in range(-10,11)))
    r2 = array.array('i',(i for i in range(-10,11)))
    r3 = array.array('i',(-1,1))
    #number of constraints per equation
    nb_eqxctr = 6
    random.seed(nseed)
    for i in range(1, num_instances+1):
        P = array.array('i',(6,12,18))
        Q = nb_eq*nb_eqxctr
        Instance_mult(random.randint(3,nb_eq),P[random.randint(0,len(P)-1)],Q,i,r1,r2,r3,min_dom,max_dom)
    