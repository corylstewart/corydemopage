from google.appengine.ext import ndb
import random


class SudokuDb(ndb.Model):
    grid = ndb.StringProperty()
    solution = ndb.StringProperty()
    level = ndb.IntegerProperty()
    user = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_puzzle_by_level(level):
        sudoku = SudokuDb()
        puzzle = sudoku.query(SudokuDb.level == level).fetch(limit=1)
        if puzzle.count == 0:
            return False
        for p in puzzle:
            return p

    @staticmethod
    def get_puzzle_by_grid(grid):
        sudoku = SudokuDb()
        puzzle = sudoku.query(SudokuDb.grid == grid)
        if puzzle.count == 0:
            return False
        for p in puzzle:
            return p

    @staticmethod
    def get_puzzle_by_solution(solution):
        sudoku = SudokuDb()
        puzzle = sudoku.query(SudokuDb.solution == solution)
        if puzzle.count == 0:
            return False
        for p in puzzle:
            return p

    @staticmethod
    def get_random_puzzle_by_level(level):
        sudoku = SudokuDb()
        puzzle = sudoku.query(SudokuDb.level == level)
        if puzzle.count == 0:
            raise LookupError
        count = random.randint(0, puzzle.count()-1)
        for p in puzzle:
            if count == 0:
                return p
            count -= 1

    @staticmethod
    def put_puzzle(grid, solution, level, user='admin'):
        exists = SudokuDb.query(SudokuDb.grid == grid)
        if exists.count() == 0:
            sudoku = SudokuDb(grid=grid,
                              solution=solution,
                              level=level,
                              user=user)
            sudoku.put()

    @staticmethod
    def delete_sudoku_db():
        sudoku = SudokuDb()
        to_delete = sudoku.query().fetch(limit=500)
        while to_delete.count != 0:
            for puzzle in to_delete:
                puzzle.key.delete()
            to_delete = sudoku.query().fetch(limit=500)
