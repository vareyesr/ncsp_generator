#from py_expression_eval import Parser
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
        list_sets = create_sum_expressions(self.P,self.Q,pool)
        #create product
        list_products = create_products(list_sets,self.nb_eq,self.P)
        #create constraint
        constraints = create_constraint(list_products,self.r1,self.r2,self.r3)
        #evaluate each constraint with a tuple (x0,x1....,xn)
        constraints,solution = evaluate_constraints(constraints,self.min_dom,self.max_dom)
        #create file
        create_file(constraints,solution,self.min_dom,self.max_dom)

def create_sum_expressions(P,Q,pool):
    sum_expressions = [set() for _ in xrange(P)]
    #fill all the sets
    for i in range(0,P):
        sum_expressions[i].add(pool[random.randint(0,len(pool)-1)])
    #fill until Q elements
    for i in range(0,Q-P):
        pool_element = pool[random.randint(0,len(pool)-1)]
        set_pos = random.randint(0,len(sum_expressions)-1)
        #if the expression is already in the set, search for a new one
        while  pool_element in sum_expressions[set_pos]:
            pool_element = pool[random.randint(0,len(pool)-1)]
        sum_expressions[set_pos].add(pool_element)
    #print 'sets of expressions: '
    #print sum_expressions
    return sum_expressions      

def create_products(list_sets,nb_eq,P):
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

def create_constraint(list_products,r1,r2,r3):
    list_expressions = [list() for _ in xrange(len(list_products))]
    for i in range(0,len(list_expressions)):
        constraint = ''
        for j in range(0,len(list_products[i])):
            if j is not 0:
                constraint = constraint+'*'
            coef = r2[random.randint(0,len(r2)-1)]
            if coef == 0:
                constraint = constraint+'('
            else:
                constraint = constraint+'('+str(coef)
            element = list_products[i][j]
            for k in element:
                coef = r1[random.randint(0,len(r1)-1)]
                if coef < 0:
                    constraint = constraint+str(coef)+'*'+k
                else:
                    constraint = constraint+'+'+str(coef)+'*'+k
            constraint = constraint+')'
        list_expressions[i] = constraint
        #print constraint
    return list_expressions

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

def create_file(constraints,solution,min_dom,max_dom):
    print '//solution: '+str(solution) 
    for i in range(0, len (constraints)):
        print constraints[i]

def create_pool(nb_var,unary_eq,nb_inst):
    #create the first n variables
    pool_list = []
    for i in range(0, nb_var):
        pool_list.append('x'+str(i))
    #additional (unary functions)
    for i in range(0,unary_eq):
        pool_list.append(unary_fun()+'('+random_var(pool_list[:nb_var])+')')
   # print 'pool list generated for the instance '+str(nb_inst)+':'
   # print pool_list
    return pool_list

def unary_fun():        
    unary = ['sin','cos','tan','exp','ln']
    return unary[random.randint(0,len(unary)-1)]

def random_var(poolvar):
    pos = random.randint(0,len(poolvar)-1)
    return poolvar[pos]    
        
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