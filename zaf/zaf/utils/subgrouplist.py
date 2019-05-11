def eval_subgroup_list(func, subgrouped_list):
    """
    Return true if func returns true according to subgrouped-list rules.

    The items in the list are applied to the function individually and using
    basic boolean algebra the full expression is evaluated. The results on the
    list level are and:ed together. Each subsgroup is assumed to contain individual
    items and the result when applying the function on these items are or:ed.
    That outcome in turn is used as a result on the top list level and is
    and:ed to the result of the other top level results.

    .. code-block:: python

        eval_subgroup_list(f, [A, (B, C)])

    f should return a boolean result. f is applied to A and the result is
    and:ed together with the result of evaluating the subgroup `(B, C)`.
    The subgroup is evaluated by applying f to B and C individually and
    or:ing the results.

    The code example expresses: ( f(A) and ( f(B) or f(C) ) )

    :param func: function to evaluate items
    :param subgrouped_list: the subgrouped-list to evaluate
    """
    for item in subgrouped_list:
        if is_subgroup(item):
            if not any(map(func, item)):
                return False
        elif not func(item):
            return False

    return True


def is_subgroup(item):
    """Subgroup is defined by a tuple."""
    return type(item) == tuple
