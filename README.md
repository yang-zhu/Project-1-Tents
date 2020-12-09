# SAT Solving Project 1: Tents

**Required Python packages:** seaborn, pyqt5
On Linux pyqt5 requires Qt to be installed. On Ubuntu, the package python3-pyqt5 is sufficient.
---

- **encoding.py**

  `encoding.py` contains the code to encode tents puzzles as CNF formulas. It can be run as script to solve puzzles as follows:
  ```
  python encoding.py <CaDiCaL path> <path to a puzzle file>
  ```
  There are several optional flags:

  -i displays the solution graphically

  -t uses the encoding that allows trees not having tents (This is unsound on its own, but we first check if the number of trees matches the prescribed number of tents in all rows/columns. If this check fails, we reject the puzzle as unsolvable without generating a formula. Otherwise the encoding has the same solutions as the normal encoding.)

  -n does not use binary addition to count tents, which leads to non-linear encoding complexity.


- **puzzle_generator.py**

  `puzzle_generator.py` generates puzzles with unique solutions. It can be run as follows:
  ```
  python puzzle_generator.py <CaDiCaL path> <Number of rows> <Number of columns>
  ```
  It outputs the puzzle on the terminal.
  The folder `puzzles` contains tents puzzles generated using this script.


- **statistics.py**

  `statistics.py` solves puzzles in the `puzzles` folder using three different configurations of `encoding.py` and measures the performance. Used measurements are number of variables, number of clauses and runtime of CaDiCaL. The script stores the results in a file called `statistics.txt`. If this file already exists in the current directory, it loads the data from the file instead of measuring again. The loaded data will be displayed as three graphs. The script can be run as follows:
  ```
  python statistics.py <CaDiCaL path>
  ```


- **gui.py**

  `gui.py` allows to create, solve and save puzzles interactively. After the grid is generated, trees can be added with left-click and removed with right-click. After a puzzle is solved, it can still be modified. The script can be run as follows:
  ```
  python gui.py <CaDiCaL path>
  ```

---

Group: Xiao Chen, Shaoying Liu, Yize Sun, Zhu Yang