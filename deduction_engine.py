__all__ = ['deduct']

def deduct(state):
    while True:
        changed = False # change all rows bellow as an or statement? or(apply_row(), ())?

        if apply_row_uniqueness(state):
            changed = True

        if apply_constraint_rules(state):
            changed = True

        if apply_agent_capacity(state):
            changed = True

        if apply_hidden_holder_rules(state):
            changed = True

        if not check_contradictions(state):
            raise ValueError("Contradiction detected during deduction")

        if not changed:
            return state


def apply_row_uniqueness(state):
    """
    Apply row-based uniqueness rules to the ownership matrix.

    Meaning:
    Each item must belong to exactly one holder.

    Rules:
    - if one holder is 1.0 for an item, set all other holders to 0.0
    - if all but one holders are 0.0 for an item, set the remaining holder to 1.0

    Returns:
    - True if any cell changed
    - False otherwise
    """
    changed = False

    for row in state.iter_item_rows():
        # Rule 1: if any holder is definitely YES, all others must be NO
        if any(value == 1.0 for value in row):
            for i, value in enumerate(row):
                target = 1.0 if value == 1.0 else 0.0
                if row[i] != target:
                    row[i] = target
                    changed = True

        # Rule 2: if exactly one holder is not definitely NO, it must be YES
        non_zero_indices = [i for i, value in enumerate(row) if value != 0.0]
        if len(non_zero_indices) == 1:
            i = non_zero_indices[0]
            if row[i] != 1.0:
                row[i] = 1.0
                changed = True

    return changed


def apply_constraint_rules(state):
    changed = False

    for holder_index, item_set in list(state.constraint_set):

        if any(state.get_relation(item, holder_index) == 1.0 for item in item_set):
            state.remove_constraint(holder_index, item_set)
            changed = True
            continue

        reduced_item_set = frozenset(
            item
            for item in item_set
            if state.get_relation(item, holder_index) != 0.0
        )

        if reduced_item_set != item_set:
            state.remove_constraint(holder_index, item_set)
            changed = True

        if len(reduced_item_set) == 0:
            # Leave contradiction detection to another pass
            continue

        if len(reduced_item_set) == 1:
            remaining_item = next(iter(reduced_item_set))

            if state.get_relation(remaining_item, holder_index) != 1.0:
                state.set_known_yes(remaining_item, holder_index)
                changed = True

            continue

        if reduced_item_set != item_set:
            state.add_constraint(holder_index, *reduced_item_set)

    return changed



def apply_agent_capacity(state):
    """
    Apply holder-capacity deduction rules for agent holders.

    Meaning:
    Each agent holder has a fixed capacity equal to the configured agent hand size.

    This pass should scan each agent holder column and apply rules such as:
    - if known YES count equals capacity, all remaining UNKNOWN/unresolved cells become NO
    - if known YES count plus UNKNOWN/unresolved count equals capacity, all remaining
      UNKNOWN/unresolved cells become YES

    Input:
    - current GameState

    Output:
    - mutates state in place as needed
    - returns True if any cell changed
    - returns False otherwise

    Notes:
    - this pass applies only to agent holders
    - hidden holder and public holder use different logic
    """
    changed = False

    for holder_index, holder in state.iter_holders(agents_only=True):
        yes_count = sum(1 for value in holder if value == 1.0)

        unresolved_items = [
            item_index
            for item_index, value in enumerate(holder)
            if 0.0 < value < 1.0
        ]

        if yes_count == state.agent_capacity:
            # Agent already has full capacity, so all unresolved cells must be NO
            for item_index in unresolved_items:
                if state.ownership[item_index][holder_index] != 0.0:
                    state.ownership[item_index][holder_index] = 0.0
                    changed = True

        elif yes_count + len(unresolved_items) == state.agent_capacity:
            # Remaining unresolved cells exactly fill the remaining capacity,
            # so they must all be YES
            for item_index in unresolved_items:
                if state.ownership[item_index][holder_index] != 1.0:
                    state.ownership[item_index][holder_index] = 1.0
                    changed = True

    return changed


def apply_hidden_holder_rules(state):
    """
    Apply special deduction rules for the hidden holder.

    Meaning:
    The hidden holder must contain exactly one item from each of three groups:
    - items 0..5
    - items 6..11
    - items 12..20

    This pass applies rules such as:
    - if one item in a group is YES in the hidden holder, all other items in
      that group become NO in the hidden holder
    - if all but one item in a group are NO in the hidden holder, the remaining
      item becomes YES in the hidden holder

    Input:
    - current GameState

    Output:
    - mutates state in place as needed
    - returns True if any cell changed
    - returns False otherwise

    Notes:
    - this pass only applies to the hidden holder
    - group definitions are hardcoded by index ranges
    """
    changed = False
    hidden_holder = state.HIDDEN_HOLDER

    groups = [
        range(0, 6),    # first group of 6
        range(6, 12),   # second group of 6
        range(12, 21),  # final group of 9
    ]

    for group in groups:
        hidden_values = [
            state.ownership[item_index][hidden_holder]
            for item_index in group
        ]

        yes_items = [
            item_index
            for item_index in group
            if state.ownership[item_index][hidden_holder] == 1.0
        ]

        non_zero_items = [
            item_index
            for item_index in group
            if state.ownership[item_index][hidden_holder] != 0.0
        ]

        # Rule 1:
        # If one item in the group is definitely YES in the hidden holder,
        # all others in the group must be NO in the hidden holder.
        if yes_items:
            yes_item = yes_items[0]
            for item_index in group:
                if item_index != yes_item and state.ownership[item_index][hidden_holder] != 0.0:
                    state.ownership[item_index][hidden_holder] = 0.0
                    changed = True

        # Rule 2:
        # If only one item in the group is not definitely NO, it must be YES.
        elif len(non_zero_items) == 1:
            remaining_item = non_zero_items[0]
            if state.ownership[remaining_item][hidden_holder] != 1.0:
                state.ownership[remaining_item][hidden_holder] = 1.0
                changed = True

    return changed


def check_contradictions(state): # TODO - check for leanness. See what I actually care about.
    """
    Check whether the current GameState violates any hard logical constraints.

    This function detects contradictions such as:
    - an item row has more than one YES
    - a live constraint becomes empty
    - an agent holder exceeds capacity
    - an agent holder cannot possibly still reach capacity
    - the hidden holder has more than one YES in a group
    - the hidden holder has no remaining possible item in a group

    Input:
    - current GameState

    Output:
    - returns True if the state is contradiction-free
    - returns False if a contradiction is detected

    Notes:
    - this function only detects contradictions
    - it does not repair the state automatically
    """
    # -------------------------------------------------------------------------
    # 1. Item-row uniqueness contradictions
    # -------------------------------------------------------------------------
    for row in state.ownership:
        yes_count = sum(1 for value in row if value == 1.0)
        if yes_count > 1:
            return False

    # -------------------------------------------------------------------------
    # 2. Constraint contradictions
    # -------------------------------------------------------------------------
    for holder_index, item_set in state.constraint_set:
        if len(item_set) == 0:
            return False

        # If every item in the constraint is definitely NO for that holder,
        # the constraint is impossible.
        if all(state.ownership[item_index][holder_index] == 0.0 for item_index in item_set):
            return False

    # -------------------------------------------------------------------------
    # 3. Agent-capacity contradictions
    # -------------------------------------------------------------------------
    for holder_index, holder in state.iter_holders(agents_only=True):
        yes_count = sum(1 for value in holder if value == 1.0)
        unresolved_count = sum(1 for value in holder if 0.0 < value < 1.0)

        # Too many definite YES values for capacity
        if yes_count > state.agent_capacity:
            return False

        # Even if all unresolved became YES, still not enough to reach capacity
        if yes_count + unresolved_count < state.agent_capacity:
            return False

    # -------------------------------------------------------------------------
    # 4. Hidden-holder group contradictions
    # -------------------------------------------------------------------------
    hidden_holder = state.HIDDEN_HOLDER
    groups = [
        range(0, 6),    # first group of 6
        range(6, 12),   # second group of 6
        range(12, 21),  # final group of 9
    ]

    for group in groups:
        values = [state.ownership[item_index][hidden_holder] for item_index in group]

        yes_count = sum(1 for value in values if value == 1.0)
        non_zero_count = sum(1 for value in values if value != 0.0)

        # More than one definite YES in a hidden-holder group
        if yes_count > 1:
            return False

        # No remaining possible item in a hidden-holder group
        if non_zero_count == 0:
            return False

    return True
