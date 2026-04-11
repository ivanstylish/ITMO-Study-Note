#!/bin/bash
export PATH="/c/Program Files/TortoiseSVN/bin:$PATH"

# =============================================================================
# svn.sh — Лабораторная работа 2, SVN
# Вариант:
#   Синий  (blue/user2): r1, r3, r9, r11, r12
#   Красный (red/user1): r0, r2, r4, r5, r6, r7, r8, r10, r13, r14
#
# Схема:
#   trunk:   r0 - r1 - r2 - r4 - r8 - r10 --[merge r13]--> r14
#                  \                                       /
#   branch2:        r3 - r5 - r6 - r7 - r9 - r11 - r12 --
# =============================================================================

# --- Создание репозитория ---
svnadmin create repo
REPO_URL="file:///D:/Undergraduate/Sophomore/FOSE/lab2/repo"
echo "- Репозиторий создан: $REPO_URL"

svn mkdir -m "project structure" $REPO_URL/trunk $REPO_URL/branches
echo "- trunk/branches созданы"

# --- Рабочая копия ---
svn checkout $REPO_URL/trunk/ wc
cd wc


# r0 — red [trunk]
cp -r ../rs/r0/* . 2>/dev/null || true
svn add *
svn commit -m "Initial commit (r0)" --username=red
echo "- Коммит r0 (red) [trunk]"


# r1 — blue [trunk]
svn rm *
cp -r ../rs/r1/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 1 (r1)" --username=blue
echo "- Коммит r1 (blue) [trunk]"


# r3 — blue: создание branch2 от trunk(r1), коммит на branch2
svn copy $REPO_URL/trunk $REPO_URL/branches/branch2 -m "Creating branch2 (r3)"
svn switch $REPO_URL/branches/branch2
svn rm *
cp -r ../rs/r3/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 3 (r3)" --username=blue
echo "- Коммит r3 (blue) [branch2 от r1]"


# r2 — red [trunk] (параллельно branch2)
svn switch $REPO_URL/trunk
svn update
svn rm *
cp -r ../rs/r2/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 2 (r2)" --username=red
echo "- Коммит r2 (red) [trunk]"


# r4 — red [trunk]
svn rm *
cp -r ../rs/r4/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 4 (r4)" --username=red
echo "- Коммит r4 (red) [trunk]"


# r5 — red [branch2]
svn switch $REPO_URL/branches/branch2
svn rm *
cp -r ../rs/r5/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 5 (r5)" --username=red
echo "- Коммит r5 (red) [branch2]"


# r6 — red [branch2]
svn rm *
cp -r ../rs/r6/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 6 (r6)" --username=red
echo "- Коммит r6 (red) [branch2]"


# r7 — red [branch2]
svn rm *
cp -r ../rs/r7/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 7 (r7)" --username=red
echo "- Коммит r7 (red) [branch2]"


# r8 — red [trunk]
svn switch $REPO_URL/trunk
svn update
svn rm *
cp -r ../rs/r8/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 8 (r8)" --username=red
echo "- Коммит r8 (red) [trunk]"


# r9 — blue [branch2]
svn switch $REPO_URL/branches/branch2
svn update
svn rm *
cp -r ../rs/r9/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 9 (r9)" --username=blue
echo "- Коммит r9 (blue) [branch2]"


# r10 — red [trunk]
svn switch $REPO_URL/trunk
svn update
svn rm *
cp -r ../rs/r10/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 10 (r10)" --username=red
echo "- Коммит r10 (red) [trunk]"


# r11 — blue [branch2]
svn switch $REPO_URL/branches/branch2
svn rm *
cp -r ../rs/r11/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 11 (r11)" --username=blue
echo "- Коммит r11 (blue) [branch2]"


# r12 — blue [branch2]
svn rm *
cp -r ../rs/r12/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 12 (r12)" --username=blue
echo "- Коммит r12 (blue) [branch2]"


# СЛИЯНИЕ branch2 -> trunk  =>  r13 (red)
svn switch $REPO_URL/trunk
svn update
svn merge $REPO_URL/branches/branch2

# Разрешение конфликтов (если есть):
# svn resolve --accept theirs-full *.java   <- принять версию branch2
# svn resolve --accept mine-full *.java     <- принять версию trunk

svn rm * --force
cp -r ../rs/r13/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 13 (r13)" --username=red
echo "- Коммит r13 (red) [merge branch2 -> trunk]"


# r14 — red [trunk]
svn rm *
cp -r ../rs/r14/* . 2>/dev/null || true
svn add *
svn commit -m "Revision 14 (r14)" --username=red
echo "- Коммит r14 (red) [trunk]"

svn update

echo ""
echo "====== ИСТОРИЯ РЕВИЗИЙ SVN ======"
svn log $REPO_URL --verbose