"""A collection of cycle detectors. 

Cycle detectors are classes of algorithms solve the halting problem
for finite state autonoma; specifically they will tell if a pure
function x = F(x') that maps from one value to the other within a
finite range of values |x| ever reaches a defined "stop" state, or
continues to cycle forever.  For this function `F(x)`; the only state
it may consider in making its decision is X.

Cycles in finite state machines are exclusively of the form
<x0, x1, x2 ... > <y0, y1, y2, y3, ... yn> where   

So for example the sequence 1, 2, 3, 4, 5 would be an example of a
terminating sequence.  This will be correctly detected as being finite
by these algorithms.

The sequence 1, 2, 3, 4, 5, 3, 4, 5, 3, 4, 5 ... is an infinite
sequence repeating 3, 4, 5 after an initial 1, and 2.  This sequence
will eventually by identified by all algorithms in this module as

The sequence 1, 2, 2, 2, 2, 3 is an example of a sequence that is
finite, but not unique.  The behavior of these algorithms on this
example are undefined.

The sequence 1, 2, 3, 4, 5, 3, 4, 5, 6, 3, 4, 5, 6, 7, ... where the
repeated section grows in length by one with each pass is not
generate by a finite state machine; this requires a machine with
unbounded memory.  The behavior of these algorithms on this class of
sequences is undefined because the set of values in the function's
range is not finite; this is not a finite state autonoma.

All cycle detection algorithms in this module share a common API; they
accept either a pair of named parameters `f` and `start` or an
algorithm specific number of instances of iterable instances, each
separately returning the same sequence.

If named parameters `f` and `start` are provided, the function `f` is
used to compute the transition from any state `X_n` to `X_(n+1)` and
`start` contains the initial state.

If positional parameters are provided, each must contain an
independent but identical implementation of the sequence being worked
with.  The number that must be provided is specific to the algorithm.

In all cases, the function will generate items from the sequence up to
the point the sequence terminates or a cycle is detected.

If a cycle is detected `CycleDetected` will be raised; if called with
`f` and `start` instead of multiple iterators, attributes `period` and
`first` containing the period of the cycle and the position of the first
repetition respectively.

"""

import functools


class CycleDetected(Exception):

    def __init__(self, period=None, first=None, *args, **kwargs):
        self.period = period
        self.first = first
        super(CycleDetected, self).__init__(*args, **kwargs)


def f_generator(f, value):
    try:
        while value is not None:
            yield value
            value = f(value)
    except StopIteration:
        pass


def _remove_kwargs_from_args(name, args, kwargs):
    try:
        value = kwargs.pop(name)
        try:
            args.remove(value)
        except ValueError:
            pass
    except LookupError:
        value = None
    return value


def _convert_f_to_seqs(n, variable=False):
    def __convert_f_t_seqs(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*seqs, **kwargs):
            seqs = list(seqs)
            f, start, m = (None, None, None)
            if 'f' in kwargs and 'start' in kwargs:
                f = _remove_kwargs_from_args('f', seqs, kwargs)
                start = _remove_kwargs_from_args('start', seqs, kwargs)
                m = _remove_kwargs_from_args('m', seqs, kwargs)
            key = _remove_kwargs_from_args(
                'key', seqs, kwargs) or (lambda x: x)

            for kwarg in kwargs:
                raise TypeError(
                    "%s() got an unexpected keyword argument %r" % (f.func_name, kwarg,))

            if seqs:
                if f is not None:
                    raise TypeError(
                        ('You may call {f.func_name} with positional parameters or '
                         'kwargs f and start, but not both').format(f=wrapped))
                if len(seqs) != (m or n):
                    raise TypeError(
                        ('{f.func_name}(*seqs=..., m={n}) must be either `m` '
                         'items in length, and all elements must independently '
                         'generate the same sequence.  *seqs={seqs}').format(
                             f=wrapped, n=m or n, seqs=seqs))
            else:
                if not f:
                    raise TypeError(
                        ('You must call {f.func_name} with either positional '
                         'parameaters or kwargs f and start').format(f=wrapped))

                seqs = [f_generator(f, start) for _ in xrange(m or n)]
            if m is None:
                return wrapped(seqs, f=f, start=start, key=key)
            return wrapped(seqs, f=f, start=start, m=m or n, key=key)
        return wrapper
    return __convert_f_t_seqs


@_convert_f_to_seqs(2)
def floyd(seqs, f=None, start=None, key=lambda x: x):
    """Floyd's Cycle Detector.

    See help(cycle_detector) for more context.

    Args:

      *args: Two iterators issueing the exact same sequence:
      -or-
      f, start: Function and starting state for finite state machine

    Yields: 

      Values yielded by sequence_a if it terminates, undefined if a
      cycle is found.

    Raises:

      CycleFound if exception is found; if called with f and `start`,
      the parametres `first` and `period` will be defined indicating
      the offset of start of the cycle and the cycle's period.
    """

    tortise, hare = seqs

    yield hare.next()
    tortise_value = tortise.next()
    hare_value = hare.next()
    while hare_value != tortise_value:
        yield hare_value
        yield hare.next()
        hare_value = hare.next()
        tortise_value = tortise.next()

    if f is None:
        raise CycleDetected()

    hare_value = f(hare_value)
    first = 0
    tortise_value = start
    while key(tortise_value) != key(hare_value):
        tortise_value = f(tortise_value)
        hare_value = f(hare_value)
        first += 1

    period = 1
    hare_value = f(tortise_value)
    while key(tortise_value) != key(hare_value):
        hare_value = f(hare_value)
        period += 1

    raise CycleDetected(period=period, first=first)


@_convert_f_to_seqs(1)
def naive(seqs, f=None, start=None, key=lambda x: x):
    """Naive cycle detector

    See help(cycle_detector) for more context.

    Args:

      sequence: A sequence to detect cyles in.

      f, start: Function and starting state for finite state machine

    Yields: 

      Values yielded by sequence_a if it terminates, undefined if a
      cycle is found.

    Raises:

      CycleFound if exception is found.  Will always generate a first
      and period value no matter which of the `seqs` or `f` interface
      is used.
    """
    history = {}
    for step, value in enumerate(seqs[0]):
        keyed = key(value)
        yield value
        if keyed in history:
            raise CycleDetected(
                first=history[keyed], period=step - history[keyed])
        history[keyed] = step


@_convert_f_to_seqs(1)
def gosper(seqs, f=None, start=None, key=lambda x: x):
    """Gosper's cycle detector

    See help(cycle_detector) for more context.

    Args:

      sequence: A sequence to detect cyles in.

      f, start: Function and starting state for finite state machine

    Yields: 

      Values yielded by sequence_a if it terminates, undefined if a
      cycle is found.

    Raises:

      CycleFound if exception is found.  Unlike Floyd and Brent's,
      Gosper's can only detect period of a cycle.  It cannot
      compute the first position
    """

    tab = []
    for c, value in enumerate(seqs[0], start=1):
        yield value
        try:
            e = tab.index(key(value))
            raise CycleDetected(
                period=c - ((((c >> e) - 1) | 1) << e))
        except ValueError:
            try:
                tab[(c ^ (c - 1)).bit_length() - 1] = key(value)
            except IndexError:
                tab.append(value)


@_convert_f_to_seqs(2)
def brent(seqs, f=None, start=None, key=lambda x: x):
    """Brent's Cycle Detector.

    See help(cycle_detector) for more context.

    Args:

      *args: Two iterators issueing the exact same sequence:
      -or-
      f, start: Function and starting state for finite state machine

    Yields: 

      Values yielded by sequence_a if it terminates, undefined if a
      cycle is found.

    Raises:

      CycleFound if exception is found; if called with f and `start`,
      the parametres `first` and `period` will be defined indicating
      the offset of start of the cycle and the cycle's period.
    """

    power = period = 1
    tortise, hare = seqs

    yield hare.next()
    tortise_value = tortise.next()
    hare_value = hare.next()
    while key(tortise_value) != key(hare_value):
        yield hare_value
        if power == period:
            power *= 2
            period = 0
            if f:
                tortise = f_generator(f, hare_value)
                tortise_value = tortise.next()
            else:
                while tortise_value != hare_value:
                    tortise_value = tortise.next()
        hare_value = hare.next()
        period += 1

    if f is None:
        raise CycleDetected()

    first = 0
    tortise_value = hare_value = start
    for _ in xrange(period):
        hare_value = f(hare_value)

    while key(tortise_value) != key(hare_value):
        tortise_value = f(tortise_value)
        hare_value = f(hare_value)
        first += 1
    raise CycleDetected(period=period, first=first)
