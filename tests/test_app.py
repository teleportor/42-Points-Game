import unittest
import datetime
import random
import time
from fractions import Fraction
from ftptsgame import FTPtsGame
from ftptsgame.exceptions import FTPtsGameError
from ftptsgame.database import DATABASE_42

class TestGameApp(unittest.TestCase):
    def test_game_app(self):
        app = FTPtsGame()
        # Status checker tests
        self.assertRaises(FTPtsGameError, app.get_current_problem)
        self.assertRaises(FTPtsGameError, app.get_current_solutions)
        self.assertRaises(FTPtsGameError, app.get_current_solution_number)
        self.assertRaises(FTPtsGameError, app.get_current_player_statistics)
        self.assertRaises(FTPtsGameError, app.get_total_solution_number)
        self.assertRaises(FTPtsGameError, app.get_elapsed_time)
        self.assertRaises(FTPtsGameError, app.solve, '123')
        self.assertRaises(FTPtsGameError, app.stop)

        # Game tests
        app.generate_problem('database', minimum_solutions=60, maximum_solutions=61)
        app.start()
        self.assertRaises(FTPtsGameError, app.start)
        self.assertRaises(FTPtsGameError, app.generate_problem, 'database', a=1, b=2)
        self.assertIs(type(app.get_elapsed_time()), datetime.timedelta)
        self.assertEqual(app.get_total_solution_number(), DATABASE_42[(3, 4, 6, 7, 12)])
        self.assertRaises(FTPtsGameError, app.solve, '')
        self.assertRaises(FTPtsGameError, app.solve, '1'*30)
        self.assertRaises(FTPtsGameError, app.solve, '1')
        self.assertRaises(FTPtsGameError, app.solve, '1+')
        self.assertRaises(FTPtsGameError, app.solve, '1+(')
        self.assertRaises(FTPtsGameError, app.solve, '42')
        self.assertRaises(FTPtsGameError, app.solve, '1+2+3+4+5+6+7+8+9-3')
        self.assertRaises(FTPtsGameError, app.solve, '-1+3')
        self.assertRaises(FTPtsGameError, app.solve, '1-(3-1)')
        self.assertRaises(FTPtsGameError, app.solve, '1**3')
        self.assertRaises(FTPtsGameError, app.solve,'-1+3')
        self.assertRaises(FTPtsGameError, app.solve,'1+3.0')
        self.assertRaises(FTPtsGameError, app.solve,'1/0')
        self.assertEqual([], app.get_current_solutions())
        self.assertIs(type(app.solve('6*7+(12-3*4)', player_id=10000)), datetime.timedelta)
        self.assertEqual(app.get_current_player_statistics(), {10000: [1]})
        self.assertRaises(FTPtsGameError, app.solve, '___123456___')
        # self.assertRaises(FTPtsGameError, app.solve('111111+ 22222 +33333 +55555'))
        # self.assertRaises(FTPtsGameError, app.solve, '6*(7 / 12)*3*4')
        self.assertRaises(FTPtsGameError, app.solve, '12/(3*4)*6*7')
        self.assertRaises(FTPtsGameError, app.solve, '6*7*(12 / (3*4))')
        self.assertRaises(FTPtsGameError, app.solve, '(12-3*4)+6*7')
        self.assertEqual(app.get_current_solution_number(), 1)
        self.assertIs(type(app.solve('       （12      +      6  /     3)  *  （7    -   4)')), datetime.timedelta)
        self.assertEqual(app.get_current_player_statistics(), {10000: [1], -1: [2]})
        self.assertEqual(['6*7+(12-3*4)', '(12+6/3)*(7-4)'], app.get_current_solutions())
        self.assertIs(type(app.solve('3*7*(12-6-4)')), datetime.timedelta)
        self.assertEqual(app.get_current_player_statistics(), {10000: [1], -1: [2, 3]})

        # Stop game
        app.stop()
        self.assertRaises(FTPtsGameError, app.get_current_problem)
        self.assertRaises(FTPtsGameError, app.get_current_solutions)
        self.assertRaises(FTPtsGameError, app.get_current_solution_number)
        self.assertRaises(FTPtsGameError, app.get_current_player_statistics)
        self.assertRaises(FTPtsGameError, app.get_total_solution_number)
        self.assertRaises(FTPtsGameError, app.get_elapsed_time)
        self.assertRaises(FTPtsGameError, app.solve, '123' )
        self.assertRaises(FTPtsGameError, app.stop)

        self.assertRaises(FTPtsGameError, app.generate_problem, method='custom')
        self.assertRaises(FTPtsGameError, app.generate_problem, method='custom', problem='12345')
        self.assertRaises(FTPtsGameError, app.generate_problem, method='custom', problem=123)
        self.assertRaises(FTPtsGameError, app.generate_problem, method='custom', problem=[0, 0, 0, 0, 0])
        self.assertRaises(FTPtsGameError, app.generate_problem, method='wrong_method', problem=[6, 7, 0, 0, 0])
        app.generate_problem('custom', problem=[6, 7, 0, 0, 0])
        app.start()
        self.assertEqual((0, 0, 0, 6, 7), app.get_current_problem())
        app.stop()

        self.assertRaises(FTPtsGameError, app.generate_problem, method='probability')
        self.assertRaises(FTPtsGameError, app.generate_problem, method='probability', prob=123)
        self.assertRaises(FTPtsGameError, app.generate_problem, method='probability', prob=[1, 2, 2])
        test_prob = [0] * len(DATABASE_42.keys())
        r = random.randint(0, len(DATABASE_42.keys()) - 1)
        test_prob[r] = 100
        app.generate_problem('probability', prob=test_prob)
        app.start()
        self.assertEqual(list(DATABASE_42.keys())[r], app.get_current_problem()) 
        app.stop()

class TestException(unittest.TestCase):
    def test_exceptions(self):
        self.assertEqual(str(FTPtsGameError(0x00, True)), 'StatusError:RequireCertainStatus[True]')
        self.assertEqual(str(FTPtsGameError(0x01, SyntaxError('Unable to parse'))), 'ProblemGenerateError:FailedtoParse[Unable to parse]')
        self.assertEqual(str(FTPtsGameError(0x02, (0, 1, 2, 3, 4))), 'ProblemGenerateError:NoSolution[(0, 1, 2, 3, 4)]')
        self.assertEqual(str(FTPtsGameError(0x04, 'wpalpek')), 'ProblemGenerateError:MethodNotFound[wpalpek]')
        self.assertEqual(str(FTPtsGameError(0x03, 10)), 'ProblemGenerateError:UnmatchedProbLength[10]')
        self.assertEqual(str(FTPtsGameError(0x10, 40)), 'FormatError:ExpressionTooLong[40]')
        self.assertEqual(str(FTPtsGameError(0x11, OverflowError('xxxx'))), 'FormatError:FailedtoParse[xxxx]')
        self.assertEqual(str(FTPtsGameError(0x12, '_ast.Add')), 'FormatError:UnallowedOperator[_ast.Add]')
        self.assertEqual(str(FTPtsGameError(0x13)), 'FormatError:DivisionByZero[-]')
        self.assertEqual(str(FTPtsGameError(0x14, 1.0)), 'FormatError:NotAnInteger[1.0]')
        self.assertEqual(str(FTPtsGameError(0x15, (1, 2, 3))), 'FormatError:UnmatchedNumber[(1, 2, 3)]')
        self.assertEqual(str(FTPtsGameError(0x20, Fraction(6, 7))), 'AnswerError:WrongAnswer[6/7]')
        self.assertEqual(str(FTPtsGameError(0x21, '6*7+0+0+0')), 'AnswerError:RepeatedAnswer[6*7+0+0+0]')
        self.assertEqual(FTPtsGameError(0x10, 123).get_details(), (0x10, 123))
        self.assertEqual(str(FTPtsGameError('not-existed', 'will-not-print-hint')), 'UnknownError:ErrnoNotFound')

class ThrottleTest(unittest.TestCase):
    
    def test_throttle(self):
        app = FTPtsGame()
        app.generate_problem('custom', problem=(1, 1, 6, 7, 12))
        app.start()
        answer = ['((1+12)-(1+6))*7', '6*(((12-7)+1)+1)', '((12*(1-1))+6)*7', '12/(1+((1-6)/7))', '12+((1-6)*(1-7))', '((1+12)-6)*(7-1)', '((1+12)-7)*(6+1)', '12-(((1+1)-7)*6)', '(6*((7+1)+1))-12']
        for ans in answer:
            time.sleep(1)
            s_time = app.solve(ans)
            self.assertLess(abs(s_time.seconds - 1), 2)
        f_time = app.stop()
        self.assertLess(abs(f_time.seconds - len(answer)), 2)
