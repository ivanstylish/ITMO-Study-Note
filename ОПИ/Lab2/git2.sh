#!/bin/bash

# Clean & backup
if [ -d ".git" ]; then
    cp -r .git .rotter
    cp .gitignore .rotterignore 2>/dev/null || true
    rm -rf .git
    rm -f .gitignore
fi
find src -type f ! -name '.keep' -delete 2>/dev/null || true

git init
echo -e "\n[merge]\n\ttool = nano" >> .git/config
git config user.name "red"
git config user.email "red@example.com"

# Create branch1 and enter into branch1
git checkout -b branch1

cat > .gitignore << 'IGNORE'
.resources
.rotter
commits
docs
src/.keep
.editorconfig
.rotterignore
git.sh
svn.sh
.gitattributes
LICENSE
README.md
IGNORE
git add .gitignore

# r0 — red [branch1]
mkdir -p src
cp -r rs/r0/* src/ 2>/dev/null || true
git add -A .
git commit -m "Initial commit (r0)"

# r4 — red [branch1]
cp -r rs/r4/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 4 (r4)"

# r8 — red [branch1]
cp -r rs/r8/* src/ 2>/dev/null || true
git add -··A .
git commit -m "Revision 8 (r8)"

# r10 — red [branch1]
cp -r rs/r10/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 10 (r10)"

# branch2：branch from r0
# Find r0 hash
R0=$(git log --oneline | grep "Initial commit" | awk '{print $1}')
git checkout -b branch2 $R0

# r1 — blue [branch2]
cp -r rs/r1/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 1 (r1)"

# Create branch3 from r1
git checkout -b branch3

# branch3：branch from r1
# r2 — red [branch3]
cp -r rs/r2/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 2 (r2)"

# r5 — red [branch3]
cp -r rs/r5/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 5 (r5)"

# r6 — red [branch3]
cp -r rs/r6/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 6 (r6)"

# r7 — red [branch3]
cp -r rs/r7/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 7 (r7)"

# continue with branch2 
git checkout branch2

# r3 — blue [branch2]
cp -r rs/r3/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 3 (r3)"

# r9 — blue [branch2] (Same files with r7)
cp -r rs/r9/* src/ 2>/dev/null || true
git add -A .
git commit --allow-empty --author="blue <blue@example.com>" -m "Revision 9 (r9)"

# r11 — blue [branch2]
cp -r rs/r11/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 11 (r11)"

# r12 — blue [branch2]
cp -r rs/r12/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 12 (r12)"

# r13: branch3 merge with branch2, turn into r13
git merge --no-commit branch3 -Xtheirs 2>/dev/null || true
mkdir -p src
cp -r rs/r13/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 13 (r13)"

# r14: branch2(including r13) merge with branch1
git checkout branch1
git merge --no-commit branch2 -Xtheirs 2>/dev/null || true
mkdir -p src
cp -r rs/r14/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 14 (r14)"

echo ""
echo "====== ГРАФ КОММИТОВ ======"
git log --graph --abbrev-commit --decorate --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(auto)%d%C(reset)' --all