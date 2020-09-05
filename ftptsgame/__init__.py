"""Main module of this project."""

from .database import DATABASE_42
from .expr_utils import build_node
import random
import datetime


class FTPtsGame(object):
    """
    The main game.

    Available methods (+ means playing, - means not playing):
    __init__(): initialization. (Entry point)
    is_playing(): show the status of current game. (+-)
    generate_problem(): generate a problem from database or on custom. (-)
    get_elapsed_time(): get the time elapsed during the game. (+)
    get_current_problem(): get current problem (tuple). (+)
    get_current_solutions(): get current solutions (list). (+)
    get_current_solution_number(): print current solution number. (+)
    get_total_solution_number(): print total solution number. (+)
    start(): start the game. (-)
    stop(): stop the game. (+)
    solve(): put forward a solution and show solution intervals. (+)
    """

    def __init__(self):
        """Start the game session, serving as an initialization."""
        self.__valid = []  # this list stores readable answers
        self.__formula = []  # this list stores converted formulas
        self.__players = []  # this list stores player statistics
        self.__playing = False  # this stores playing status

    def __status_check(self, required_status: bool = True):
        """A status checker."""
        if required_status != self.is_playing():
            raise PermissionError('Required status: %s' % required_status)

    def is_playing(self) -> bool:
        """Incicate the game is started or not."""
        return self.__playing

    def get_elapsed_time(self) -> datetime.timedelta:
        """Get elapsed time between solutions. Effective when playing."""
        self.__status_check(required_status=True)
        elapsed = datetime.datetime.now() - self.__timer
        return elapsed

    def generate_problem(self, **kwargs) -> tuple:
        """Generate a random problem from the range of numbers."""
        minimum = kwargs['minimum'] if 'minimum' in kwargs else 0
        maximum = kwargs['maximum'] if 'maximum' in kwargs else 13
        problem = [random.randint(minimum, maximum) for _ in range(5)]
        return problem

    def get_current_problem(self) -> tuple:
        """Get current problem. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__problem

    def get_current_solutions(self) -> list:
        """Get current valid solutions. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__valid

    def get_current_solution_number(self) -> int:
        """Get the number of current solutions. Effective when playing."""
        self.__status_check(required_status=True)
        return len(self.__valid)

    def get_total_solution_number(self) -> int:
        """Get the number of total solutions. Effective when playing."""
        self.__status_check(required_status=True)
        return DATABASE_42[self.__problem]

    def get_current_player_statistics(self) -> dict:
        """Get current player statistics. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__players

    def __validate_repeated(self, node: str):
        """Validate distinguishing expressions. Private method."""
        for ind in range(0, len(self.__formula)):
            cmp_node = self.__formula[ind]
            if cmp_node == node or cmp_node.simplify() == node.simplify():
                raise LookupError(self.__valid[ind])

    def solve(self, math_expr: str, player_id: int = -1) -> datetime.timedelta:
        """Put forward a solution and show solution intervals if correct."""
        self.__status_check(required_status=True)

        replace_table = [
            ('×', '*'), ('x', '*'), ('÷', '/'), (' ', ''),
            ('\n', ''), ('\r', ''), ('（', '('), ('）', ')'),
        ]
        for src, dest in replace_table:
            math_expr = math_expr.replace(src, dest)

        if len(math_expr) >= 30:
            raise OverflowError('Maximum parsing length exceeded.')

        node = build_node(math_expr)
        math_expr_value = node.evaluate()
        user_input_numbers = node.extract()
        if math_expr_value != 42:
            raise ArithmeticError(str(math_expr_value))
        if tuple(sorted(user_input_numbers)) != self.__problem:
            print(user_input_numbers)
            raise ValueError('Unmatched input numbers.')

        self.__validate_repeated(node)
        self.__formula.append(node)
        self.__valid.append(math_expr)
        elapsed = self.get_elapsed_time()
        interval = elapsed - self.__last
        self.__last = elapsed
        self.__players.append((player_id, interval))
        return interval

    def start(self):
        """Start the game. Effective when not playing."""
        self.__status_check(required_status=False)
        self.__valid = []
        self.__formula = []
        self.__players = []
        self.__timer = datetime.datetime.now()
        self.__last = datetime.timedelta(seconds=0)  # A tag for each solution.
        self.__playing = True

    def stop(self) -> datetime.timedelta:
        """Stop the game. Effective when playing."""
        self.__status_check(required_status=True)
        elapsed = self.get_elapsed_time()
        self.__playing = False
        return elapsed
