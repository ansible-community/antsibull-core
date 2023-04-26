# BSD 2-clause license (see LICENSES/BSD-2-Clause.txt)
# SPDX-FileCopyrightText: Ansible Project
# SPDX-License-Identifier: BSD-2-Clause

# pylint:disable=missing-module-docstring,no-else-break


# NB: a copy of this function exists in ../../modules/core/async_wrapper.py. Ensure any
# changes are propagated there.
def _filter_non_json_lines(data):
    """
    Used to filter unrelated output around module JSON output, like messages from
    tcagetattr, or where dropbear spews MOTD on every single command (which is nuts).

    Filters leading lines before first line-starting occurrence of '{' or '[', and filter all
    trailing lines after matching close character (working from the bottom of output).
    """
    warnings = []

    # Filter initial junk
    lines = data.splitlines()

    for start, line in enumerate(lines):
        line = line.strip()
        if line.startswith("{"):
            endchar = "}"
            break
        elif line.startswith("["):
            endchar = "]"
            break
    else:
        raise ValueError("No start of json char found")

    # Filter trailing junk
    lines = lines[start:]

    for reverse_end_offset, line in enumerate(reversed(lines)):
        if line.strip().endswith(endchar):
            break
    else:
        raise ValueError("No end of json char found")

    if reverse_end_offset > 0:
        # Trailing junk is uncommon and can point to things the user might
        # want to change.  So print a warning if we find any
        trailing_junk = lines[len(lines) - reverse_end_offset :]
        for line in trailing_junk:
            if line.strip():
                warnings.append(
                    "Module invocation had junk after the JSON data: %s"
                    % "\n".join(trailing_junk)
                )
                break

    lines = lines[: (len(lines) - reverse_end_offset)]

    return ("\n".join(lines), warnings)
