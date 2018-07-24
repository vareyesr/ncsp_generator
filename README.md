# A Numerical Constraint Satisfaction Problem (NCSP) generator

The generator constructs a (non)linear square systems with n variables and m equality constraints.

## Getting Started

In order to run the generator, you must have python 2.x (probably not compatible with python3.x).
On ubuntu you can install it with:

```
~$ sudo apt-get install python 2.7
```

Also note that files *config.txt* and *generator.py* must be in the same folder before the execution.

## The generator

The generator uses a user-config *config.txt* file in order to define the type of instance that the user wants to create. It is advisable to only modify this file, but if you have some suggestions related to the generator you can do a pull request.
The generator has some parameters that can be modified in the config file, which are explained below:

- **sets** simply used to create various configurations at the same time.
- **n** number of variables.
- **m** number of equations.
- **dom** it generates a random number that lies in the interval [a,b] for each variable. Then this vector is used to evaluate each contraint and set it equal to the corresponding value. In this way we insure that the problem has at least one solution.
- **poolsize** defines the size of the pool. This pool includes the set of **n** variables plus powers of variables (square or cube) randomly generated or unary functions defined by this variables ,i.e. sin(x1), exp(x1), etc (See **type_pool**). Note that poolsize must be greater or equal than **n**.
- **type_bench** defines the type of benchmark. For multiplication of sums you have to set it to *sum*, for sum of unary functions you have to set it to *trigo* and for sums of multiplications you have to set it to *mul*.
- **type_pool** defines the type of the other **poolsize-n** variables to be include in the poolsize. For powers just use *power* and for unary just use *trigo*.
- **rnd_seed** the seed.
- **r1** list of multiplication coefficients, random selected for some variable of the pool.
- **r2** list of constants accompanying each expression.
- **r3** list of exponents for the sums.
- **r4** list of exponents for the variables in the pool when **type_bench** is defined as *power*
- **nb_inst** number of instances of each set.
- **P** total number of sums (or multiplications) in the NCSP.
- **Q** total number of terms in the NCSP.

To execute the generator, just type in your terminal:

```
~$ python generator.py
```

## Authors

* **Victor Reyes** - PUCV  [WWW](https://sites.google.com/view/csvictor-reyes)
* **Ignacio Araya** - PUCV