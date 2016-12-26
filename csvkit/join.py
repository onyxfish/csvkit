#!/usr/bin/env python


def _get_keys(rows, column_index, lowercase=False):
    """
    Get keys from rows as keys in a dictionary (i.e. unordered), given the key column index.
    """
    pairs = ((r[column_index], True) for r in rows)
    return CaseInsensitiveDict(pairs) if lowercase else dict(pairs)


def _get_mapped_keys(rows, column_index, case_insensitive=False):
    mapped_keys = CaseInsensitiveDict() if case_insensitive else {}

    for r in rows:
        key = r[column_index]

        if key in mapped_keys:
            mapped_keys[key].append(r)
        else:
            mapped_keys[key] = [r]

    return mapped_keys

def _lower(key):
    """Transforms a string to lowercase, leaves other types alone."""
    keyfn = getattr(key, 'lower', None)
    return keyfn() if keyfn else key


def sequential_join(left_rows, right_rows, header=True):
    """
    Join two tables by aligning them horizontally without performing any filtering.
    """
    len_left_headers = len(left_rows[0])
    len_right_headers = len(right_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = iter(right_rows[1:])
    else:
        output = []

    for left_row in left_rows:
        try:
            right_row = next(right_rows)
            output.append(left_row + right_row)
        except StopIteration:
            output.append(left_row + [u''] * len_right_headers)

    for right_row in right_rows:
        output.append([u''] * len_left_headers + right_row)

    return output


def inner_join(left_rows, left_column_id, right_rows, right_column_id, header=True, ignore_case=False):
    """
    Execute an inner join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Map right rows to keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id, ignore_case)

    for left_row in left_rows:
        len_left_row = len(left_row)

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        left_key = left_row[left_column_id]

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)

    return output


def full_outer_join(left_rows, left_column_id, right_rows, right_column_id, header=True, ignore_case=False):
    """
    Execute full outer join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])
    len_right_headers = len(right_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Get left keys
    left_keys = _get_keys(left_rows, left_column_id, ignore_case)

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id, ignore_case)

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)
        else:
            output.append(left_row + ([u''] * len_right_headers))

    for right_row in right_rows:
        right_key = right_row[right_column_id]

        if right_key not in left_keys:
            output.append(([u''] * len_left_headers) + right_row)

    return output


def left_outer_join(left_rows, left_column_id, right_rows, right_column_id, header=True, ignore_case=False):
    """
    Execute left outer join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])
    len_right_headers = len(right_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id, ignore_case)

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)
        else:
            output.append(left_row + ([u''] * len_right_headers))

    return output


def right_outer_join(left_rows, left_column_id, right_rows, right_column_id, header=True, ignore_case=False):
    """
    Execute right outer join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Get left keys
    left_keys = _get_keys(left_rows, left_column_id, ignore_case)

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id, ignore_case)

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)

    for right_row in right_rows:
        right_key = right_row[right_column_id]

        if right_key not in left_keys:
            output.append(([u''] * len_left_headers) + right_row)

    return output



class CaseInsensitiveDict(dict):
    """
    Adapted from http://stackoverflow.com/a/32888599/1583437
    """
    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(_lower(key))

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(_lower(key), value)

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(_lower(key))

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(_lower(key))

    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(_lower(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(_lower(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(_lower(key), *args, **kwargs)

    def update(self, single_arg=None, **kwargs):
        super(CaseInsensitiveDict, self).update(self.__class__(single_arg))
        super(CaseInsensitiveDict, self).update(self.__class__(**kwargs))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)
