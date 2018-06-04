#
#Created:       20/05/2018
#Last update:   24/05/2018
#Authors:       Victor Reyes, Ignacio Araya
#
from __future__ import division
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import ConfigParser
import random
from sets import Set
import math
import array
import numpy as np
import operator
import re
import copy
import os
import sys

class NumericStringParser(object):

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val

class Instance_creator:
    def __init__(self,nb_var,nb_eq,poolsize,P,Q,nb_inst,r1,r2,r3,r4,min_dom,max_dom,sett,type_bench):
        self.nb_var = nb_var
        self.nb_eq = nb_eq
        self.poolsize = poolsize
        self.P = P 
        self.Q = Q
        self.nb_inst = nb_inst
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.min_dom = min_dom
        self.max_dom = max_dom 
        self.sett = sett
        self.type_bench = type_bench
        #create pool
        pool = create_pool(nb_eq,poolsize,nb_inst,r4,self.type_bench)
        #create sets
        list_sets = create_pool_expressions(self.P,self.Q,pool)
        #create product
        list_expressions = create_expressions(list_sets,self.nb_eq,self.P)
        #create constraint
        constraints = create_constraints(list_expressions,self.r1,self.r2,self.r3,self.type_bench)
        #evaluate each constraint with a tuple (x0,x1....,xn)
        constraints,solution = evaluate_constraints(constraints,self.min_dom,self.max_dom)
        #create file
        create_file(constraints,solution,self.min_dom,self.max_dom,self.nb_inst,self.nb_var,self.sett)

def create_pool_expressions(P,Q,pool):
    expressions = [set() for _ in xrange(P)]
    #fill all the sets
    for i in range(0,P):
        expressions[i].add(pool[random.randint(0,len(pool)-1)])
    #fill until Q elements
    for i in range(0,Q-P):
        pool_element = pool[random.randint(0,len(pool)-1)]
        set_pos = random.randint(0,len(expressions)-1)
        #if the expression is already in the set, search for a new one
        while  pool_element in expressions[set_pos]:
            pool_element = pool[random.randint(0,len(pool)-1)]
            set_pos = random.randint(0,len(expressions)-1)
        expressions[set_pos].add(pool_element)
    #print 'sets of expressions: '
    return expressions      

def create_expressions(list_sets,nb_eq,P):
    list_factors = [list() for _ in xrange(nb_eq)]
    #fill all the constraints
    for i in range(0,nb_eq):
        element = list_sets[random.randint(0,len(list_sets)-1)]
        list_factors[i].append(element)
        list_sets.remove(element)
    #fill with the remaining elements
    for i in range(0,P-nb_eq):
        element = list_sets[random.randint(0,len(list_sets)-1)]
        list_factors[random.randint(0,nb_eq-1)].append(element)
        list_sets.remove(element)
    return list_factors

def create_constraints(list_products,r1,r2,r3,type_bench):
    list_constraints = [list() for _ in xrange(len(list_products))]
    for i in range(0,len(list_constraints)):
        constraint = ''
        if type_bench == 'sum':
            for j in range(0,len(list_products[i])):
                if j is not 0:
                    constraint = constraint+'*'
                coef = r2[random.randint(0,len(r2)-1)]
                if coef == 0:
                    constraint = constraint+'('
                else:
                    constraint = constraint+'('+str(int(coef))
                element = list_products[i][j]
                for k in element:
                    coef = r1[random.randint(0,len(r1)-1)]
                    if coef < 0:
                        constraint = constraint+str(int(coef))+'*'+k
                    else:
                        constraint = constraint+'+'+str(int(coef))+'*'+k
                exp = r3[random.randint(0,len(r3)-1)]
                if exp != 1:
                    constraint = constraint+')^('+str(int(exp))+')'
                else:
                    constraint = constraint+')'
        else:
            for j in range(0,len(list_products[i])):
                if j is not 0:
                    constraint = constraint+'+'
                coef = r2[random.randint(0,len(r2)-1)]
                constraint = constraint+'('+str(int(coef))
                element = list_products[i][j]
                for k in element:
                    coef = r1[random.randint(0,len(r1)-1)]
                    if coef < 0:
                        constraint = constraint+'*('+k+')^('+str(int(coef))+')'
                    else:
                         constraint =constraint+'*('+k+')^'+str(int(coef))
                constraint = constraint+')'         
        list_constraints[i] = constraint
    return list_constraints

def evaluate_constraints(constraints,min_dom,max_dom):
    evaluation = copy.copy(constraints)
    solution = np.zeros(len(constraints))
    #a random solution is generated
    for i in range(0, len (constraints)):
        solution[i] = random.uniform(min_dom,max_dom) 
    #we evaluate each constraint in the solution in order to guarantee that the problem is not empty
    #first we replace the variables for sol
    for i in range(0, len (evaluation)):
        for j in range(0, len (evaluation)):
            evaluation[i] = re.sub(r'x'+str(j),str(solution[j]),evaluation[i])    
    nsp = NumericStringParser()
    for i in range(0, len (constraints)):
        result = nsp.eval(evaluation[i])
        constraints[i] = constraints[i]+' = '+str(result)
    return constraints, solution

def create_file(constraints,solution,min_dom,max_dom,nb_inst,nb_var,sett):
    #for i in range(0, len (constraints)):
    #   print constraints[i]

    if not os.path.exists('benchs'):
        os.makedirs('benchs')

    if not os.path.exists('benchs/'+sett):
        os.makedirs('benchs/'+sett)

    completeName = os.path.join('benchs/'+sett, 'inst'+ "%03d" % (nb_inst)+ ".txt")         
    f = open(completeName,"w+")
    f.write('//'+'One known solution for this problem is:\n')
    f.write('//')
    for i in range (0, len(solution)):
        f.write(str(solution[i])+',')
    f.write('\nVariables\n\n')
    for i in range (0,nb_var):
        f.write('x'+str(i)+' in '+ '[1,1e8];\n')
    f.write('\nConstraints\n\n')
    for i in range (0,len(constraints)):
        f.write(constraints[i]+';\n')
    f.write('end')


def create_pool(nb_var,poolsize,nb_inst,r4,type_bench):
    #create the first n variables
    pool_list = []
    unary_exp = []
    pool_set = set()
    for i in range(0, nb_var):
        unary_exp.append('x'+str(i))
    #additional (unary functions)
    if type_bench == 'sum':
        for i in range (0, nb_var):
            exponent = int(r4[random.randint(0,len(r4)-1)])
            if exponent == 1:
                expression = 'x'+str(i)
            else:
                expression = 'x'+str(i)+'^'+str(exponent)
            pool_list.append(expression)
            pool_set.add(expression)
        fns = [power_fun]
    else:
        for i in range (0, nb_var):
            expression = 'x'+str(i)
            pool_list.append(expression)
            pool_set.add(expression)
        fns = [unary_fun]

    current_size = len(pool_list)
    for i in range(0,poolsize-nb_var): 
        expression = random.choice(fns)(unary_exp,r4)
        while expression in pool_set:
            expression = random.choice(fns)(unary_exp,r4) 
        pool_list.append(expression)
        pool_set.add(expression)
    return pool_list

def unary_fun(unary_exp,r4):        
    #unary = ['exp']
    unary = ['sin','cos','tan','exp']
    #unary = ['sin','cos','tan','exp','ln']
    return unary[random.randint(0,len(unary)-1)]+'('+unary_exp[random.randint(0,len(unary_exp)-1)]+')'

def power_fun(unary_exp,r4):
    exponent = int(r4[random.randint(0,len(r4)-1)])
    if exponent == 1:     
        return unary_exp[random.randint(0,len(unary_exp)-1)]
    else:
        return unary_exp[random.randint(0,len(unary_exp)-1)]+'^'+str(exponent)    
def random_var(poolvar):
    pos = random.randint(0,len(poolvar)-1)
    return poolvar[pos]    

class Params:
    def __init__(self, configParser):
        self.configParser=configParser
        self.set_parameters("default")


    def set_parameters(self, name):
        self.set = name

        if configParser.has_option(name,  'n'):
            self.n = int(configParser.get(name, 'n'))

        if configParser.has_option(name,  'm'):
            self.m = int(configParser.get(name, 'm'))

        if configParser.has_option(name,  'dom'):
            self.lb,self.ub = configParser.get(name, 'dom').split()
            self.lb = int(self.lb)
            self.ub = int(self.ub)

        if configParser.has_option(name,  'poolsize'):
            self.poolsize = int(configParser.get(name, 'poolsize'))

        if configParser.has_option(name,  'type_bench'):
            self.type_bench = str(configParser.get(name, 'type_bench'))

        if configParser.has_option(name,  'rnd_seed'):
            self.rnd_seed = int(configParser.get(name, 'rnd_seed'))

        if configParser.has_option(name,  'r1'):
            self.r1 = [float(x) for x in configParser.get(name, 'r1').split()]
            self.r2 = [float(x) for x in configParser.get(name, 'r2').split()]
            self.r3 = [float(x) for x in configParser.get(name, 'r3').split()]
            self.r4 = [float(x) for x in configParser.get(name, 'r4').split()]

        if configParser.has_option(name, 'nb_inst'):
            self.nb_inst = int(configParser.get(name, 'nb_inst'))

        if configParser.has_option(name, 'P'):
            self.P = int(configParser.get(name, 'P'))

        if configParser.has_option(name, 'Q'):
            self.Q = int(configParser.get(name, 'Q'))
     
if __name__ == '__main__':

    configParser = ConfigParser.RawConfigParser()   
    configParser.read("config.txt")

    p = Params(configParser)
    random.seed(p.rnd_seed)

    for sett in configParser.get('default', 'sets').split():
        p.set_parameters('default')
        p.set_parameters(sett)

        #number of constraints per equation
        for i in range(1, p.nb_inst+1):
            Instance_creator(p.n,p.m,p.poolsize,p.P,p.Q,i,p.r1,p.r2,p.r3,p.r4,p.lb,p.ub,p.set,p.type_bench)
        if p.nb_inst == 1:
            print str(p.nb_inst)+' instance has been created!'
        else:
            print str(p.nb_inst)+' instances had been created!'