import logging
import os
import re
from enum import Enum
from datetime import datetime

from typing import (
    Callable,
    Iterable,
    Tuple,
    List,
    TypeVar,
    Union,
)
import itertools

T = TypeVar('T')


class Satisfiablity(str, Enum):
    SAT = "SAT"
    UNSAT = "UNSAT"
    UNKNOWN = "UNKNOWN"  # Actual result unknown
    UNSURE = "UNSURE"  # Could not find satisfiability


def satisfiability_of_output(output: str) -> Satisfiablity:
    # TODO liklely faster to do 'sat' in output.lower() or something
    if re.search('Unsat', output):
        return Satisfiablity.UNSAT
    elif re.search('Sat', output):
        return Satisfiablity.SAT
    elif re.search('Unknown', output):
        return Satisfiablity.UNKNOWN
    return Satisfiablity.UNSURE


def valid_smt(filename: Union[bytes, str]) -> bool:
    if os.fspath(filename).endswith('.smt2'):
        return True
    else:
        return False

def exclude(bad_values: List[str]) -> Callable[[Union[bytes, str]], bool]:
    def do_exclusion(dirname: Union[bytes, str]) -> bool:
        if type(dirname) == bytes:
            dirname = dirname.decode('utf8')
        pathname = os.path.basename(os.fspath(dirname))
        if pathname == '':
            pathname = os.path.basename(os.fspath(dirname[:-1]))
        return pathname not in bad_values
    return do_exclusion


def partition(pred: Callable[[T], bool], iterable: Iterable[T]) -> Tuple[List[T], List[T]]:
    "Use a predicate to partition entries into true entries and false entries"
    # partition(is_odd, range(10)) --> 1 3 5 7 9 and 0 2 4 6 8
    t1, t2 = itertools.tee(iterable)
    return list(filter(pred, t2)), list(itertools.filterfalse(pred, t1))


def now_string() -> str:
    """Returns the time in a %Y-%m-%d-%H-%M-%S formatted string"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d-%H-%M-%S")


def setup_logging_default():
    logging.basicConfig(filename=f'log-{now_string()}.txt', level=logging.INFO)


def setup_logging_debug():
    logging.basicConfig(filename=f'log-{now_string()}.txt', level=logging.DEBUG)


def flatten(lst):
    """Flattens a list so that any elements that were lists are replaces by the elements of that list.
    ex: [1, [[2], 3]] -> [1, 2, 3]"""

    output = []
    for x in lst:
        if type(x) != list:
            output.append(x)
        else:
            output.extend(flatten(x))
    return output
