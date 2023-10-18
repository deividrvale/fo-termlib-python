from dataclasses import dataclass
from term import Term
import term as tm


@dataclass
class Rule:
    lhs: Term
    rhs: Term
