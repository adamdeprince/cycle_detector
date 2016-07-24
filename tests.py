import functools
import signal
from unittest import TestCase

from cycle_detector import brent, CycleDetected, floyd, f_generator, gosper, naive


def timeout(wrapped):
    class Timeout(Exception):
        pass

    def raise_timeout(signum, frame):
        raise Timeout()

    @functools.wraps(wrapped)
    def _timeout(*args, **kwargs):
        signal.signal(signal.SIGALRM, raise_timeout)
        signal.alarm(1)
        try:
            return wrapped(*args, **kwargs)
        finally:
            signal.alarm(0)
    return _timeout


class CycleDetectorCase(object):

    def detector(self, seq_func=None, f=None, start=None, m=None):
        if f is not None:
            seqs = []
        else:
            seqs = [seq_func() for _ in xrange(self.detector_seq_count)]
        return self.detector_func()(*seqs, f=f, start=start)

    @timeout
    def test_enumerates_non_cyclic_sequence_correctly(self):
        seq = lambda: iter(xrange(10))
        self.assertEquals(
            list(self.detector(seq)),
            list(seq()))

    @timeout
    def test_detects_cycle_in_seqeunce(self):
        def seq():
            for value in xrange(4):
                yield value
            while True:
                for value in xrange(4, 10):
                    yield value

        with self.assertRaises(CycleDetected) as e:
            for x in self.detector(seq):
                pass
        self.assertFalse(hasattr(e, 'period'))
        self.assertFalse(hasattr(e, 'first'))

    @timeout
    def test_detects_termination_in_state_transfer_function(self):
        f = {1: 2,
             2: 3,
             3: 4,
             4: 5,
             5: 6,
             6: 7,
             7: 8,
             8: 9}.get
        self.assertEquals(list(self.detector(f=f, start=1)),
                          list(range(1, 10)))

    @timeout
    def test_detects_cycle_in_state_transfer_function(self):
        f = {1: 2,
             2: 3,
             3: 4,
             4: 5,
             5: 6,
             6: 7,
             7: 8,
             8: 9,
             9: 4}.get
        with self.assertRaises(CycleDetected) as e:
            for x in self.detector(f=f, start=1):
                pass
        self.assertEquals(e.exception.period, 6)
        self.assertEquals(e.exception.first, 3)


class PeriodOnlyCycleDetectorCase(CycleDetectorCase):

    @timeout
    def test_detects_cycle_in_state_transfer_function(self):
        f = {1: 2,
             2: 3,
             3: 4,
             4: 5,
             5: 6,
             6: 7,
             7: 8,
             8: 9,
             9: 4}.get
        with self.assertRaises(CycleDetected) as e:
            for x in self.detector(f=f, start=1):
                pass
        self.assertEquals(e.exception.period, 6)
        self.assertIsNone(e.exception.first)


class TestFloydCycleDetector(TestCase, CycleDetectorCase):

    def detector_func(self):
        return floyd

    detector_seq_count = 2


class TestBrentsCycleDetector(TestCase, CycleDetectorCase):

    def detector_func(self):
        return brent

    detector_seq_count = 2


class TestGosperCycleDetector(TestCase, PeriodOnlyCycleDetectorCase):

    def detector_func(self):
        return gosper

    detector_seq_count = 1


class TestNaiveCycleDetector(TestCase, CycleDetectorCase):

    def detector_func(self):
        return naive

    detector_seq_count = 1
