cycle_detector
--------------

A pure python module implementing a variety of cycle detectors. 

What's a cycle
--------------

Imagine you have a function F(x) that accepts a single value x from a
finite set of possiable values, returns a single value in the same
finite set of possiable values and maintains no state between calls.
If you called one of the states `"done"` and wrote this bit of code:


```
    state = start
    while state != done:
        state = f(state)
```

whether the code ends or not depends on whether or not `f(x)` has a
cycle when begining with the `start` state.

So if the transitions from state to state went like this:

```
   start -> a -> b -> c -> d -> e -> done
```

the sequence is said to halt.  But if the sequence looked like this:

```
   start -> a -> b -> c -> d -> e -> b -> c -> d -> e - > b -> c ....
```

the sequence is said to have a "cycle"; in this case the "cycle" is
`b->c->d->e`.


Usage
-----

All of the cycle detectors in this module can operate from either a
function and start value, or a sequence of geneated values.  Some
cycle detectors, noteably floyd's turtle and hare algorithum, require
more than one indepenent, but otherwise identical, generator if they
are to use the generator interface.


## Using the geneator interface

```
>>> from cycle_detector import gosper


>>> def has_cycle():
...    yield 1
...    yield 2
...    yield 3
...    while True:
...    	  yield 4
...	  yield 5 

>>> def has_no_cycle():
...    yield 1
...    yield 2
...    yield 3


>>> l = list(list(gospher(has_no_cycle())))
<l = [1, 2, 3]>

>>> l = list(gospher(has_cycle()))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
CycleDetected

>>> l = list(floyd(has_cycle(), has_cycle()))
```

## Using the function interface

If you use the function interface insteat 

```
>>> from cycle_detector import floyd
>>> f = {1: 2,
             2: 3, 
             3: 4,
             4: 5,
             5: 6,
             6: 7,
             7: 8,
             8: 9}.get
>>> try: for x in floyd(f=f, start=1)
... except CycleDetected as e:
>>> print e.period, e.first
6 3
```


Cycle Detectors compared
------------------------



name    |  Time               |  Memory    |  Streams  |  Can find λ  | Can find  μ
------- | ------------------- | ---------- | --------- | ------------ | ------------
niave   | O(λ+μ)              | O(λ+μ)     | 1         | Yes          | Yes
gospher | O((λ+μ)lg(λ+μ))     | O(lg(λ+μ)) | 1         | Yes          | No
floyd   | O(λ+μ)              | O(1)       | 2         | Only with F  | Only with F
brent   | O(λ+μ)(~30% sooner) | O(1)       | 2         | Only with F  | Only with F
        

Gripes
------

# You lied about memory consumption.

I wrote this bit of code and my memory consumption skyrockets:

```
    a, b = itertools.tee(foo())
    for x in floyd(a, b):
        pass
```

Floyd and brent require independent streams; `itertools.tee` creates
two branches, everytime you call one branch in advance of the other,
the generated value will be saved for later consumption.  Using
itertools.tee requires O(λ + μ) memory; you might as well use the
`niave` and have the benefit of earlier detection and accurate one
pass determination of values λ and μ.  


# But your code is solving the halting problem.  You can't do that! 

Yes, while the halting problem is not computable for Turing machines,
it is computable for finite state autonoma.  If your F function looks something like this:

```
    def F(x):
      value = 0
      while True:
        yield value
        value += 1
```

none of these cycle detectors will ever stop.

# Your code doesn't work for this simple sequence

``` 
    start -> SomeObject<1> -> SomeObject<1> -> done 
```

It doens't work because your first `SomeObject<1>` isn't really equal to your
second `SomObject<1>`; a function `f(x)` that can do this is hiding state
someplace.  Your objects have to support `__eq__` and `__hash__` properly, or 
you have to fully expose your object state via a `key` method or rewriting the 
object to something like this:

```
    start -> (1, SomeObject<0>) -> (1, SomeObject<1>) -> done
```




    
       

