#from py_expression_eval import Parser
import ConfigParser
import random
from sets import Set
import math
import array
import numpy as np

class Instance_mult:
    def __init__(self,nb_var,nb_eq,P,Q,nb_inst,r1,r2,r3,min_dom,max_dom):
        self.nb_var = nb_var
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
        #list_sets = create_sum_expressions(self.P,self.Q,pool)

def create_sum_expressions(P,pool):
    sum_expressions = [set() for _ in xrange(P)]
    #fill all the sets
    for i in range(0,P):
        sum_expressions[i].add(pool[random.randint(0,len(pool)-1)])
    #fill until Q elements
  #  for i in range(0,P-Q):

        
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

    configParser = ConfigParser.RawConfigParser()   
    configParser.read("config.txt")
    n = int(configParser.get('base', 'n'))
    m = int(configParser.get('base', 'm'))

    lb,ub = configParser.get('base', 'dom').split()
    lb = int(lb)
    ub = int(ub)

    poolsize = int(configParser.get('base', 'poolsize'))
    rnd_seed = int(configParser.get('base', 'rnd_seed'))

    r1 = [float(x) for x in configParser.get('base', 'r1').split()]
    r2 = [float(x) for x in configParser.get('base', 'r2').split()]
    r3 = [float(x) for x in configParser.get('base', 'r3').split()]

    nb_inst = int(configParser.get('set1', 'nb_inst'))

    P = int(configParser.get('set1', 'P'))
    Q = int(configParser.get('set1', 'Q'))

    #number of constraints per equation
    random.seed(rnd_seed)
    for i in range(1, nb_inst+1):
        Instance_mult(n,m,P,Q,i,r1,r2,r3,lb,ub)
    