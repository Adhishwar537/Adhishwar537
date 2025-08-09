from abc import ABC, abstractmethod
from typing import Optional
from omath.core.problem import Problem
from omath.core.results import Result


class Solver(ABC):
    @abstractmethod
    def supports(self, problem: Problem) -> bool:
        raise NotImplementedError

    @abstractmethod
    def solve(self, problem: Problem) -> Result:
        raise NotImplementedError

    def try_solve(self, problem: Problem) -> Optional[Result]:
        if not self.supports(problem):
            return None
        return self.solve(problem)