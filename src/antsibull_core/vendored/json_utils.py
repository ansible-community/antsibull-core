# BSD 2-clause license (see LICENSES/BSD-2-Clause.txt)
# SPDX-FileCopyrightText: Ansible Project
# SPDX-License-Identifier: BSD-2-Clause
#
# This is borrowed from
# https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/json_utils.py.
# Minor changes were made to add type hints and follow Python 3 best practices.

"""
Utilities to sanitize JSON output.
"""

from __future__ import annotations


def _filter_non_json_lines(data: str) -> tuple[str, list[str]]:
    '''
    Used to filter unrelated output around module JSON output, like messages from
    tcagetattr, or where dropbear spews MOTD on every single command (which is nuts).

    Filters leading lines before first line-starting occurrence of '{' or '[', and filter all
    trailing lines after matching close character (working from the bottom of output).
    '''
    warnings = []

    # Filter initial junk
    lines = data.splitlines()

    for start, line in enumerate(lines):
        line = line.strip()
        if line.startswith('{'):
            endchar = '}'
            break
        if line.startswith('['):
            endchar = ']'
            break
    else:
        raise ValueError('No start of json char found')

    # Filter trailing junk
    lines = lines[start:]

    for reverse_end_offset, line in enumerate(reversed(lines)):
        if line.strip().endswith(endchar):
            break
    else:
        raise ValueError('No end of json char found')

    if reverse_end_offset > 0:
        # Trailing junk is uncommon and can point to things the user might
        # want to change.  So print a warning if we find any
        trailing_junk = lines[len(lines) - reverse_end_offset:]
        for line in trailing_junk:
            if line.strip():
                junk = '\n'.join(trailing_junk)
                warnings.append(f'Module invocation had junk after the JSON data: {junk}')
                break

    lines = lines[:(len(lines) - reverse_end_offset)]

    return ('\n'.join(lines), warnings)
