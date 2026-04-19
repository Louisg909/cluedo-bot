
import pytest

from state import GameState, NO, YES, UNKNOWN


# -----------------------------------------------------------------------------
# Initialisation tests
# -----------------------------------------------------------------------------

def test_init_sets_basic_counts_correctly():
    state = GameState(n_agents=4)

    assert state.n_agents == 4
    assert state.n_holders == 6  # hidden + public + 4 agents
    assert state.agent_capacity == (21 - 3) // 4


def test_init_creates_ownership_matrix_with_correct_shape():
    state = GameState(n_agents=3)

    assert len(state.ownership) == 21
    assert all(len(row) == 5 for row in state.ownership)  # 3 agents + hidden + public


def test_init_sets_all_cells_to_unknown():
    state = GameState(n_agents=3)

    for row in state.ownership:
        for cell in row:
            assert cell == UNKNOWN


def test_init_starts_with_empty_constraint_set():
    state = GameState(n_agents=3)

    assert state.constraint_set == set()


def test_init_rejects_invalid_agent_count():
    with pytest.raises(ValueError):
        GameState(n_agents=0)


# -----------------------------------------------------------------------------
# Basic mutation tests
# -----------------------------------------------------------------------------

def test_set_known_yes_sets_cell_to_yes():
    state = GameState(n_agents=3)

    state.set_known_yes(4, 2)

    assert state.get_relation(4, 2) == YES


def test_set_known_no_sets_cell_to_no():
    state = GameState(n_agents=3)

    state.set_known_no(4, 2)

    assert state.get_relation(4, 2) == NO


def test_set_unknown_sets_cell_to_unknown():
    state = GameState(n_agents=3)

    state.set_known_yes(4, 2)
    state.set_unknown(4, 2)

    assert state.get_relation(4, 2) == UNKNOWN


def test_set_known_yes_raises_if_cell_already_no():
    state = GameState(n_agents=3)

    state.set_known_no(4, 2)

    with pytest.raises(ValueError):
        state.set_known_yes(4, 2)


def test_set_known_no_raises_if_cell_already_yes():
    state = GameState(n_agents=3)

    state.set_known_yes(4, 2)

    with pytest.raises(ValueError):
        state.set_known_no(4, 2)


def test_set_holder_row_yes_and_others_no_resolves_entire_row():
    state = GameState(n_agents=3)

    state.set_holder_row_yes_and_others_no(7, 3)

    row = state.get_item_row(7)
    assert row[3] == YES

    for holder_index, value in enumerate(row):
        if holder_index != 3:
            assert value == NO


def test_initialise_user_hand_places_cards_in_first_agent_holder():
    state = GameState(n_agents=3)

    state.initialise_user_hand(1, 5, 9)

    user_holder = state.FIRST_AGENT_HOLDER

    for item_index in (1, 5, 9):
        row = state.get_item_row(item_index)
        assert row[user_holder] == YES
        assert row.count(YES) == 1
        assert row.count(NO) == state.n_holders - 1


def test_initialise_public_fact_resolves_entire_row_to_public_holder():
    state = GameState(n_agents=3)

    state.initialise_public_fact(8)

    row = state.get_item_row(8)
    assert row[state.PUBLIC_HOLDER] == YES
    assert row.count(YES) == 1
    assert row.count(NO) == state.n_holders - 1


def test_initialise_hidden_exclusion_sets_hidden_holder_to_no():
    state = GameState(n_agents=3)

    state.initialise_hidden_exclusion(6)

    assert state.get_relation(6, state.HIDDEN_HOLDER) == NO


# -----------------------------------------------------------------------------
# Constraint tests
# -----------------------------------------------------------------------------

def test_add_constraint_adds_constraint_to_set():
    state = GameState(n_agents=3)

    state.add_constraint(3, 1, 2, 3)

    assert (3, frozenset({1, 2, 3})) in state.constraint_set


def test_add_constraint_rejects_empty_constraint():
    state = GameState(n_agents=3)

    with pytest.raises(ValueError):
        state.add_constraint(3)


def test_add_constraint_rejects_invalid_holder():
    state = GameState(n_agents=3)

    with pytest.raises(ValueError):
        state.add_constraint(99, 1, 2, 3)


def test_add_constraint_rejects_invalid_item():
    state = GameState(n_agents=3)

    with pytest.raises(ValueError):
        state.add_constraint(3, 1, 2, 99)


def test_add_constraint_deduplicates_identical_constraints():
    state = GameState(n_agents=3)

    state.add_constraint(3, 1, 2, 3)
    state.add_constraint(3, 1, 2, 3)

    assert len(state.constraint_set) == 1


def test_remove_constraint_removes_existing_constraint():
    state = GameState(n_agents=3)

    state.add_constraint(3, 1, 2, 3)
    state.remove_constraint(3, [1, 2, 3])

    assert state.constraint_set == set()


def test_replace_constraint_replaces_correctly():
    state = GameState(n_agents=3)

    state.add_constraint(3, 1, 2, 3)
    state.replace_constraint(3, [1, 2, 3], 3, [2, 3])

    assert (3, frozenset({1, 2, 3})) not in state.constraint_set
    assert (3, frozenset({2, 3})) in state.constraint_set


def test_clear_constraints_for_holder_removes_only_that_holders_constraints():
    state = GameState(n_agents=3)

    state.add_constraint(2, 1, 2)
    state.add_constraint(3, 4, 5)
    state.clear_constraints_for_holder(2)

    assert (2, frozenset({1, 2})) not in state.constraint_set
    assert (3, frozenset({4, 5})) in state.constraint_set


def test_get_constraints_returns_copy_not_original():
    state = GameState(n_agents=3)

    state.add_constraint(2, 1, 2)
    constraints = state.get_constraints()
    constraints.add((3, frozenset({4, 5})))

    assert (3, frozenset({4, 5})) not in state.constraint_set


# -----------------------------------------------------------------------------
# Query tests
# -----------------------------------------------------------------------------

def test_get_item_row_returns_correct_row():
    state = GameState(n_agents=3)

    state.set_known_yes(0, 2)
    row = state.get_item_row(0)

    assert len(row) == state.n_holders
    assert row[2] == YES


def test_get_holder_column_returns_correct_column():
    state = GameState(n_agents=3)

    state.set_known_yes(0, 2)
    state.set_known_no(1, 2)

    column = state.get_holder_column(2)

    assert len(column) == 21
    assert column[0] == YES
    assert column[1] == NO


def test_get_possible_holders_excludes_no_cells():
    state = GameState(n_agents=3)

    state.set_known_no(4, 0)
    state.set_known_no(4, 1)

    possible = state.get_possible_holders(4)

    assert 0 not in possible
    assert 1 not in possible
    assert set(possible) == {2, 3, 4}


def test_get_possible_items_for_holder_excludes_no_cells():
    state = GameState(n_agents=3)

    state.set_known_no(0, 2)
    state.set_known_no(1, 2)

    possible = state.get_possible_items_for_holder(2)

    assert 0 not in possible
    assert 1 not in possible
    assert len(possible) == 19


def test_get_known_items_for_holder_returns_only_yes_items():
    state = GameState(n_agents=3)

    state.set_known_yes(0, 2)
    state.set_known_yes(5, 2)
    state.set_known_no(9, 2)

    known = state.get_known_items_for_holder(2)

    assert set(known) == {0, 5}


def test_get_unknown_items_for_holder_returns_only_unknown_items():
    state = GameState(n_agents=3)

    state.set_known_yes(0, 2)
    state.set_known_no(1, 2)

    unknown = state.get_unknown_items_for_holder(2)

    assert 0 not in unknown
    assert 1 not in unknown
    assert len(unknown) == 19


def test_get_constraints_for_holder_filters_correctly():
    state = GameState(n_agents=3)

    state.add_constraint(2, 1, 2)
    state.add_constraint(3, 4, 5)

    constraints = state.get_constraints_for_holder(2)

    assert constraints == {(2, frozenset({1, 2}))}


# -----------------------------------------------------------------------------
# Resolution / contradiction tests
# -----------------------------------------------------------------------------

def test_is_resolved_cell_false_for_unknown_and_true_for_yes_or_no():
    state = GameState(n_agents=3)

    assert state.is_resolved_cell(0, 2) is False

    state.set_known_no(0, 2)
    assert state.is_resolved_cell(0, 2) is True


def test_is_fully_resolved_for_item_true_when_exactly_one_yes_and_rest_no():
    state = GameState(n_agents=3)

    state.set_holder_row_yes_and_others_no(6, 4)

    assert state.is_fully_resolved_for_item(6) is True


def test_is_fully_resolved_for_item_false_when_unknowns_remain():
    state = GameState(n_agents=3)

    state.set_known_yes(6, 4)

    assert state.is_fully_resolved_for_item(6) is False


def test_has_direct_contradiction_false_for_clean_state():
    state = GameState(n_agents=3)

    assert state.has_direct_contradiction() is False


def test_has_direct_contradiction_true_if_row_has_multiple_yes_values():
    state = GameState(n_agents=3)

    state.ownership[4][2] = YES
    state.ownership[4][3] = YES

    assert state.has_direct_contradiction() is True


# -----------------------------------------------------------------------------
# Snapshot tests
# -----------------------------------------------------------------------------

def test_snapshot_returns_independent_copy():
    state = GameState(n_agents=3)
    state.set_known_yes(1, 2)
    state.add_constraint(2, 1, 2, 3)

    snap = state.snapshot()

    state.set_known_no(2, 2)
    state.add_constraint(3, 4, 5)

    assert snap["ownership"][1][2] == YES
    assert snap["ownership"][2][2] == UNKNOWN
    assert (3, frozenset({4, 5})) not in snap["constraint_set"]
