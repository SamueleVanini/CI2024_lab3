from functools import cache
import logging
from typing import Callable, NamedTuple
import numpy as np
import random

from random import choice
from tqdm.auto import tqdm
from itertools import chain
from utilities import execution_time, counter

from data_structure import SvanniPriorityQueue, Item, State
from exp.squillero_code import squillero_initial

PUZZLE_DIM = 6
# RANDOMIZE_STEPS = 100_000
RANDOMIZE_STEPS = 200
# added only for reproducibility
random.seed(42)


def configure_logging(console_level=logging.INFO, utility_level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(console_level)
    utility_logger = logging.getLogger("utilities")
    utility_logger.setLevel(utility_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s", style="%")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


class Action(NamedTuple):
    pos1: tuple[int]
    pos2: tuple[int]


GOAL = State(np.array(list(range(1, PUZZLE_DIM**2)) + [0]).reshape((PUZZLE_DIM, PUZZLE_DIM)))


def available_actions(state: State) -> list[Action]:
    x, y = [int(_[0]) for _ in np.where(state.value == 0)]
    actions = list()
    if x > 0:
        actions.append(Action((x, y), (x - 1, y)))
    if x < PUZZLE_DIM - 1:
        actions.append(Action((x, y), (x + 1, y)))
    if y > 0:
        actions.append(Action((x, y), (x, y - 1)))
    if y < PUZZLE_DIM - 1:
        actions.append(Action((x, y), (x, y + 1)))
    return actions


@counter
def do_action(state: State, action: Action) -> State:
    new_state = State(state)
    new_state.value[action.pos1], new_state.value[action.pos2] = (
        new_state.value[action.pos2],
        new_state.value[action.pos1],
    )
    new_state.lock_data()
    return new_state


def get_init_state():
    state = State(GOAL)
    for r in tqdm(range(RANDOMIZE_STEPS), desc="Randomizing"):
        state = do_action(state, choice(available_actions(state)))
    init_state = State(state)
    init_state.lock_data()
    return init_state


@execution_time
def a_star(
    state: State, state_cost: dict[int, int], fronteer: SvanniPriorityQueue, distance: Callable[[State], int]
) -> State:

    # visited_state must contain only the the cost needed to get to that state
    state_cost[state] = 0

    while not check_goal(state):

        valid_actions = available_actions(state)

        for a in valid_actions:

            new_state = do_action(state, a)

            new_state_cost = state_cost[state] + 1

            if new_state not in fronteer and new_state not in state_cost:
                # create the cost cost (father + 1)
                state_cost[new_state] = new_state_cost
                p = state_cost[new_state] + distance(new_state)
                fronteer.put(Item(p, new_state), block=False)

            elif new_state in fronteer and state_cost[new_state] > new_state_cost:
                # update the fronteer (the state is in the fronteer but we the cost of an old path, update it to push algo to convergence faster)
                p = state_cost[new_state] + distance(new_state)
                # fronteer.replace(Item(p, new_state), Item(new_state_cost, new_state))

                state_cost[new_state] = new_state_cost

        state = fronteer.get(block=False).data

    return state


@cache
def missing_tiles(state: State) -> int:
    needed_steps = 0
    correct_value = 1
    iter = chain.from_iterable(state.value)
    max_value = PUZZLE_DIM**2
    for value in iter:
        if value and value != (correct_value % max_value):
            needed_steps += 1
        correct_value += 1
    return needed_steps


@cache
def manhattan_distance(state: State) -> int:
    tot_sum = 0
    correct_value = 1
    matrix = state.value
    for i in range(PUZZLE_DIM):
        for j in range(PUZZLE_DIM):
            if matrix[i, j] != correct_value and matrix[i, j]:
                cx = (matrix[i, j] - 1) / PUZZLE_DIM
                cy = (matrix[i, j] - 1) % PUZZLE_DIM
                tot_sum += abs(cx - i) + abs(cy - j)
            correct_value += 1
    return tot_sum


@cache
def check_goal(state: State) -> bool:
    correct_value = 1
    iter = chain.from_iterable(state.value)
    max_value = PUZZLE_DIM**2
    for value in iter:
        if value != (correct_value % max_value):
            return False
        correct_value += 1
    return True


# It's a bit strange but with the other version the code runs faster, probabily due to the need of array creation in the middle
# of the operation (malloc is still a heavy operation)

# def check_goal(state: State) -> bool:
#     return np.all(state.current_value == GOAL.current_value)

# def distance(state: State) -> int:
#     return np.sum((state.current_value != GOAL.current_value) & (state.current_value > 0))

N = PUZZLE_DIM


def getInvCount(arr):
    arr1 = []
    for y in arr:
        for x in y:
            arr1.append(x)
    arr = arr1
    inv_count = 0
    for i in range(N * N - 1):
        for j in range(i + 1, N * N):
            # count pairs(arr[i], arr[j]) such that
            # i < j and arr[i] > arr[j]
            if arr[j] and arr[i] and arr[i] > arr[j]:
                inv_count += 1

    return inv_count


# find Position of blank from bottom
def findXPosition(puzzle):
    # start from bottom-right corner of matrix
    for i in range(N - 1, -1, -1):
        for j in range(N - 1, -1, -1):
            if puzzle[i][j] == 0:
                return N - i


# This function returns true if given
# instance of N*N - 1 puzzle is solvable
def isSolvable(puzzle):
    # Count inversions in given puzzle
    invCount = getInvCount(puzzle)

    # If grid is odd, return true if inversion
    # count is even.
    if N & 1:
        return ~(invCount & 1)

    else:  # grid is even
        pos = findXPosition(puzzle)
        if pos & 1:
            return ~(invCount & 1)
        else:
            return invCount & 1


if __name__ == "__main__":
    logger = configure_logging(logging.INFO, logging.INFO)

    init_state = get_init_state()

    logger.info(init_state.value)
    do_action.num_calls = 0
    state_cost = dict[int, int]()
    fronteer = SvanniPriorityQueue()
    logger.info("Solver starting with %s", manhattan_distance.__qualname__)
    final_state = a_star(init_state, state_cost, fronteer, manhattan_distance)
    logger.info("state=%s", final_state.value)
    logger.info("number of calls=%d", do_action.num_calls)
    logger.info("cost=%d", state_cost[final_state])

    # state_cost.clear()
    # fronteer = SvanniPriorityQueue()

    # logger.info("Solver starting with %s", missing_tiles.__qualname__)
    # do_action.num_calls = 0
    # final_state = a_star(init_state, state_cost, fronteer, missing_tiles)
    # logger.info("state=%s", final_state.value)
    # logger.info("number of calls=%d", do_action.num_calls)
    # logger.info("cost=%d", state_cost[final_state])
