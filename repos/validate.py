import fileinput
import sys
from unidiff import PatchSet

added = 0
removed = 0

MERGE = False
diff_lines = False
for line in fileinput.input():
    if line.startswith("commit"):
        _, commit_hash = line.split()

    if line.startswith("Merge:"):
        MERGE = True
        parents = line.split()[1:]
        assert len(parents) == 2, "Only merge two branches at a time: %s" % repr(parents)

    if diff_lines:
        diff_lines.append(line)

    if line.startswith('diff'):
        diff_lines = [line]


patch = PatchSet(diff_lines)
print "======= the patch ====="
print patch
print "======= the patch ====="

changes = removed + added
leading_zeros = len(str(changes)) * '0'

assert commit_hash.startswith(leading_zeros), "%s doesn't start with %s for %s changes" % (commit_hash, leading_zeros, changes)
