class GameState:
    """
    Canonical Markov-like state for constrained item allocation.

    Holders are indexed as:
    0 -> hidden holder
    1 -> public holder
    2.. -> agent holders in fixed order

    Items are indexed by a fixed external convention.

    This state stores current hard knowledge and unresolved constraints.
    It does not store event history.

    Hard-state convention:
    - 0.0 means definite 0.0
    - 1.0 means definite 1.0
    - any value strictly between 0.0 and 1.0 is unresolved
    - in MVP_v1, unresolved cells are initialised to 0.5
    - in MVP_v2, unresolved cells may be replaced by probabilistic values
    """

    N_ITEMS = 21
    HIDDEN_HOLDER = 0 # hidden holder index
    PUBLIC_HOLDER = 1 # public holder index
    FIRST_AGENT_HOLDER = 2 # the holder using the tool's index

    def __init__(self, n_agents: int, user_hand:set, public_hand:set=None):
        if n_agents < 1:
            raise ValueError("n_agents must be at least 1")

        self.n_agents = n_agents
        # Number of active agent holders.
        # Invariant:
        # - agent holders are indexed in [2, 2 + n_agents)

        self.n_holders = n_agents + 2
        # Total number of holders.
        # Invariants:
        # - holder 0 is always the hidden holder
        # - holder 1 is always the public holder
        # - holders 2.. are agent holders in fixed order

        self.agent_capacity = (self.N_ITEMS - 3) // n_agents
        # Number of items held by each agent holder.
        # Invariants:
        # - hidden holder always has 3 items, handled by deduction logic
        # - public holder contains the remainder and should be fully resolved in setup
        # - each agent holder is assumed to have exactly this many items

        self.ownership = [
            [0.5 for _ in range(self.n_holders)]
            for _ in range(self.N_ITEMS)
        ]
        # ownership[item_index][holder_index] = value in [0.0, 1.0]
        #
        # Hard interpretation:
        # - 0.0 => definite 0.0
        # - 1.0 => definite 1.0
        # - strictly between 0.0 and 1.0 => unresolved
        #
        # Invariants:
        # - item_index is in [0, N_ITEMS)
        # - holder_index is in [0, n_holders)
        # - values are floats in [0.0, 1.0]
        # - in MVP_v1, only 0.0, 0.5, 1.0 should appear
        # - in MVP_v2, unresolved cells may take non-binary probability values
        # - if ownership[i][h] becomes 1.0, deduction logic should force
        #   ownership[i][k] = 0.0 for all k != h
        # - if all but one holder for item i are 0.0, deduction logic may infer
        #   the final holder is 1.0

        self.constraint_set = set()
        # Set of constraints of the form:
        #   (holder_index, frozenset({item_index, item_index, ...}))
        #
        # Meaning:
        #   holder_index contains at least one item from the given set.
        #
        # Invariants:
        # - holder_index is valid
        # - item set is non-empty
        # - all item indices are valid
        # - duplicate logical constraints do not coexist
        # - constraints store only still-relevant current information
        # - if one item in the set becomes 1.0 for that holder, deduction logic
        #   may remove the constraint as satisfied
        # - if an item becomes impossible for that holder (0.0), deduction logic
        #   may shrink the constraint
        # - if only one item remains in the set, deduction logic may infer that
        #   item is 1.0 for that holder
        #
        # MVP_v2 note:
        # - this remains a hard logical constraint store
        # - probabilistic logic may inspect it, but should not replace it

        self.initialise_user_hand(*user_hand)

        if public_hand != None:
            self.initialise_public_hand(*public_hand)

    # -------------------------------------------------------------------------
    # Validation helpers
    # -------------------------------------------------------------------------

    def _validate_item_index(self, item_index: int) -> None:
        if not (0 <= item_index < self.N_ITEMS):
            raise ValueError(f"invalid item_index: {item_index}")

    def _validate_holder_index(self, holder_index: int) -> None:
        if not (0 <= holder_index < self.n_holders):
            raise ValueError(f"invalid holder_index: {holder_index}")

    def _validate_state_value(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"invalid state value: {value}")

    # -------------------------------------------------------------------------
    # Setup / initialisation interactions
    # -------------------------------------------------------------------------

    def set_known_yes(self, item_index: int, holder_index: int) -> None:
        """
        Set a hard known 1.0 relation.

        MVP_v1:
        - used for setup facts and later deductions / direct observations

        MVP_v2:
        - unchanged
        - probability layer should treat this as certainty
        """
        self._validate_item_index(item_index)
        self._validate_holder_index(holder_index)

        current = self.ownership[item_index][holder_index]
        if current == 0.0:
            raise ValueError("contradiction: cannot set 1.0 where state is already 0.0")

        self.ownership[item_index][holder_index] = 1.0

    def set_known_no(self, item_index: int, holder_index: int) -> None:
        """
        Set a hard known 0.0 relation.

        MVP_v1:
        - used for setup facts and later deductions / direct exclusions

        MVP_v2:
        - unchanged
        - probability layer should treat this as impossibility
        """
        self._validate_item_index(item_index)
        self._validate_holder_index(holder_index)

        current = self.ownership[item_index][holder_index]
        if current == 1.0:
            raise ValueError("contradiction: cannot set 0.0 where state is already 1.0")

        self.ownership[item_index][holder_index] = 0.0

    def set_unknown(self, item_index: int, holder_index: int) -> None:
        """
        Low-level correction/reset operation.

        This does not restore any previously removed constraints or re-run deduction.
        It should only be used in controlled edit/reset workflows.

        MVP_v2:
        - unresolved cells may later be assigned a non-binary probability,
          but this method resets the cell to the baseline unresolved value.
        """
        self._validate_item_index(item_index)
        self._validate_holder_index(holder_index)
        self.ownership[item_index][holder_index] = 0.5 # TODO this will conflict with probabilities in MVP_v2

    def set_probability(self, item_index: int, holder_index: int, value: float) -> None: # should be purely "UPDATE PROBABILITY" as I am not setting it - that will be done by the probability engine. I will just give it the new information and it will determine how it should be updated
        """
        Set a soft probability-like value for an unresolved cell.

        Intended for MVP_v2.

        Rules:
        - value must be in [0.0, 1.0]
        - value must not overwrite a hard 0.0 or 1.0 with a conflicting non-binary value
        - hard facts should still be written with set_known_no / set_known_yes
        """
        self._validate_item_index(item_index)
        self._validate_holder_index(holder_index)
        self._validate_state_value(value)

        current = self.ownership[item_index][holder_index]

        if current == 0.0 and value != 0.0:
            raise ValueError("cannot overwrite hard 0.0 with non-hard probability")
        if current == 1.0 and value != 1.0:
            raise ValueError("cannot overwrite hard 1.0 with non-hard probability")

        self.ownership[item_index][holder_index] = value

    def initialise_public_fact(self, item_index: int) -> None:
        """
        Mark an item as belonging to the public holder.

        MVP_v1:
        - convenience setup helper
        - fully resolves the item row
        """
        self.set_holder_row_yes_and_others_no(item_index, self.PUBLIC_HOLDER)

    def initialise_hidden_exclusion(self, item_index: int) -> None:
        """
        Mark an item as definitely 0.0 belonging to the hidden holder.
        """
        self.set_known_no(item_index, self.HIDDEN_HOLDER)

    # -------------------------------------------------------------------------
    # Constraint interactions
    # -------------------------------------------------------------------------

    def add_constraint(self, holder_index: int, *item_indices: int) -> None:
        """
        Add an unresolved at-least-one constraint.

        Meaning:
        holder_index contains at least one of the given item_indices.
        """
        self._validate_holder_index(holder_index)

        item_set = frozenset(item_indices)
        if not item_set:
            raise ValueError("constraint must contain at least one item")

        for item_index in item_set:
            self._validate_item_index(item_index)

        self.constraint_set.add((holder_index, item_set))

    def remove_constraint(self, holder_index: int, item_indices) -> None:
        """
        Remove a specific constraint if present.
        """
        self._validate_holder_index(holder_index)

        item_set = frozenset(item_indices)
        for item_index in item_set:
            self._validate_item_index(item_index)

        self.constraint_set.discard((holder_index, item_set))

    def replace_constraint(
        self,
        old_holder_index: int,
        old_item_indices,
        new_holder_index: int,
        new_item_indices,
    ) -> None:
        """
        Replace one constraint with another.
        """
        self.remove_constraint(old_holder_index, old_item_indices)
        self.add_constraint(new_holder_index, *new_item_indices)

    def clear_constraints_for_holder(self, holder_index: int) -> None:
        """
        Remove all constraints attached to a holder.
        """
        self._validate_holder_index(holder_index)
        self.constraint_set = {
            constraint
            for constraint in self.constraint_set
            if constraint[0] != holder_index
        }

    # -------------------------------------------------------------------------
    # Read/query interactions
    # -------------------------------------------------------------------------

    def get_relation(self, item_index: int, holder_index: int) -> float:
        """
        Return the current value for one item-holder pair.

        Interpretation:
        - 0.0 => hard 0.0
        - 1.0 => hard 1.0
        - strictly between 0.0 and 1.0 => unresolved / soft
        """
        self._validate_item_index(item_index)
        self._validate_holder_index(holder_index)
        return self.ownership[item_index][holder_index]

    def get_item_row(self, item_index: int) -> list[float]:
        """
        Return the full state row for an item across all holders.
        """
        self._validate_item_index(item_index)
        return list(self.ownership[item_index])
    
    def iter_item_rows(self):
        for row in list(self.ownership):
            yield row

    def get_holder_column(self, holder_index: int) -> list[float]:
        """
        Return the full state column for a holder across all items.
        """
        self._validate_holder_index(holder_index)
        return [self.ownership[item_index][holder_index] for item_index in range(self.N_ITEMS)]

    def iter_holders(self, agents_only=False):
        """
        Yield (holder_index, holder_column) pairs.
    
        If agents_only is True, yield only agent holders.
        Otherwise, yield all holders.
    
        The yielded holder_column is a copy/snapshot of the current column.
        Mutations must be written back through state.ownership[item_index][holder_index].
        """
        start = self.FIRST_AGENT_HOLDER if agents_only else 0
    
        for holder_index in range(start, self.n_holders):
            holder = [
                self.ownership[item_index][holder_index]
                for item_index in range(self.N_ITEMS)
            ]
            yield holder_index, holder
            

    def get_constraints(self):
        """
        Return a snapshot of the current unresolved constraints.
        """
        return set(self.constraint_set)

    def get_constraints_for_holder(self, holder_index: int):
        """
        Return all unresolved constraints attached to a holder.
        """
        self._validate_holder_index(holder_index)
        return {
            constraint
            for constraint in self.constraint_set
            if constraint[0] == holder_index
        }

    def get_possible_holders(self, item_index: int) -> list[int]:
        """
        Return holder indices for which the item is not currently ruled out.

        MVP_v1:
        - means relation != 0.0

        MVP_v2:
        - still useful as feasible-space input
        """
        self._validate_item_index(item_index)
        return [
            holder_index
            for holder_index in range(self.n_holders)
            if self.ownership[item_index][holder_index] != 0.0
        ]

    def get_possible_items_for_holder(self, holder_index: int) -> list[int]:
        """
        Return item indices not currently ruled out for a holder.
        """
        self._validate_holder_index(holder_index)
        return [
            item_index
            for item_index in range(self.N_ITEMS)
            if self.ownership[item_index][holder_index] != 0.0
        ]

    def get_known_items_for_holder(self, holder_index: int) -> list[int]:
        """
        Return item indices currently known 1.0 for a holder.
        """
        self._validate_holder_index(holder_index)
        return [
            item_index
            for item_index in range(self.N_ITEMS)
            if self.ownership[item_index][holder_index] == 1.0
        ]

    def get_unknown_items_for_holder(self, holder_index: int) -> list[int]:
        """
        Return item indices still unresolved for a holder.

        MVP_v1:
        - this will usually mean value == 0.5

        MVP_v2:
        - this means any value strictly between 0.0 and 1.0
        """
        self._validate_holder_index(holder_index)
        return [
            item_index
            for item_index in range(self.N_ITEMS)
            if 0.0 < self.ownership[item_index][holder_index] < 1.0
        ]

    def is_fully_resolved_for_item(self, item_index: int) -> bool:
        """
        Check whether an item has exactly one hard 1.0 and all others hard 0.0.
        """
        self._validate_item_index(item_index)
        row = self.ownership[item_index]
        return row.count(1.0) == 1 and all(value in (0.0, 1.0) for value in row)

    def is_resolved_cell(self, item_index: int, holder_index: int) -> bool:
        """
        Check whether a cell is hard-resolved.

        Returns True only for exact 0.0 or exact 1.0.
        """
        value = self.get_relation(item_index, holder_index)
        return value == 0.0 or value == 1.0

    # -------------------------------------------------------------------------
    # Bulk/setup convenience interactions
    # -------------------------------------------------------------------------

    def set_holder_row_yes_and_others_no(self, item_index: int, holder_index: int) -> None:
        """
        Set one 1.0 for an item and force 0.0 for every other holder.
        """
        self.set_known_yes(item_index, holder_index)
        for other_holder_index in range(self.n_holders):
            if other_holder_index != holder_index:
                self.set_known_no(item_index, other_holder_index)
    
    def set_all_nos(self, holder_indicies:Set, item_indecies):
        for holder in holder_indicies:
            for item in item_indicies:
                self.set_known_no(item, holder) # should error if they are already a yes

    def initialise_user_hand(self, *item_indices: int) -> None:
        for item_index in item_indices:
            self.set_holder_row_yes_and_others_no(item_index, 2) # index 2 is the user holder


    def initialise_public_hand(self, *item_indices: int) -> None:
        for item_index in item_indices:
            self.set_holder_row_yes_and_others_no(item_index, 1) # index 1 is the public holder

    # -------------------------------------------------------------------------
    # Validation / integrity interactions
    # -------------------------------------------------------------------------

    def has_direct_contradiction(self) -> bool:
        """
        Lightweight integrity check for obvious structural contradictions.

        Checks:
        - an item row has more than one hard 1.0
        - constraint_set contains invalid or empty constraints
        """
        for item_index in range(self.N_ITEMS):
            yes_count = sum(1 for value in self.ownership[item_index] if value == 1.0)
            if yes_count > 1:
                return True

        for holder_index, item_set in self.constraint_set:
            if not item_set:
                return True
            if not (0 <= holder_index < self.n_holders):
                return True
            for item_index in item_set:
                if not (0 <= item_index < self.N_ITEMS):
                    return True

        return False

    def snapshot(self):
        """
        Return a state snapshot.

        MVP_v2 note:
        - ownership may contain non-binary unresolved values
        """
        return {
            "n_agents": self.n_agents,
            "n_holders": self.n_holders,
            "agent_capacity": self.agent_capacity,
            "ownership": [row[:] for row in self.ownership],
            "constraint_set": set(self.constraint_set),
        }
