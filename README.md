# Lab 3

## Usage

To run the laboratory:
- create a virtual environment with `python -m venv <ENV NAME>`
- activate the environment (on linux and mac os use the command `source <ENV NAME>/bin/activate`)
- run the command `python main.py`

## Results

All the results proposed are obtained using the `A*` algorithm: 

| Puzzle size | Distance | Randomized steps | Path Cost | State explored | Execution time |
| :-: | :-: | :-: | :-: | :-: | :-: |
| 3 x 3 | Manhattan | 10.000 | 24 | 6501 | 0.1593s |
| 4 x 4 | Manhattan | 5.000 | 34 | 52.247 | 0.4772s | 
| 5 x 5 | Manhattan | 200 | 56 | 8.412.858 | 137.9832 | 
| 6 x 6 | Manhattan | 200 | NONE | NONE | NONE |
| 7 x 7 | Manhattan | 200 | NONE | NONE | NONE |

## External links:

Some ideas/code has been taken from:
- [Squillero's code](https://github.com/squillero/computational-intelligence/blob/master/2022-23/8-puzzle.ipynb)
- [Check if puzzle is solvable](https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/)