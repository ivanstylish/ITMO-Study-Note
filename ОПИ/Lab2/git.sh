#!/bin/bash

# --- Очистка и бэкап ---
if [ -d ".git" ]; then
    cp -r .git .rotter
    cp .gitignore .rotterignore 2>/dev/null || true
    rm -rf .git
    rm -f .gitignore
    echo "- Создан бэкап .git"
fi

find src -type f ! -name '.keep' -delete 2>/dev/null || true
echo "- src очищен"

# --- Инициализация ---
git init
echo "- git init"

echo -e "\n[merge]\n\ttool = nano" >> .git/config

git config user.name "red"
git config user.email "red@example.com"
echo "- Пользователь red настроен"

git checkout -b branch1

# --- .gitignore ---
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
echo "- .gitignore создан"


# r0 — red [branch1]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r0/* src/ 2>/dev/null || true
git add -A .
git commit -m "Initial commit (r0)"
echo "- Коммит r0 (red) [branch1]"


# r1 — blue [branch1]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r1/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 1 (r1)"
echo "- Коммит r1 (blue) [branch1]"


# r3 — blue: создание branch2 от r1, первый коммит на branch2
git checkout -b branch2
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r3/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 3 (r3)"
echo "- Коммит r3 (blue) [branch2 от r1]"


# r2 — red [branch1] (параллельно branch2)
git checkout branch1
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r2/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 2 (r2)"
echo "- Коммит r2 (red) [branch1]"


# r4 — red [branch1]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r4/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 4 (r4)"
echo "- Коммит r4 (red) [branch1]"


# r5 — red [branch2]
git checkout branch2
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r5/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 5 (r5)"
echo "- Коммит r5 (red) [branch2]"


# r6 — red [branch2]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r6/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 6 (r6)"
echo "- Коммит r6 (red) [branch2]"


# r7 — red [branch2]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r7/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 7 (r7)"
echo "- Коммит r7 (red) [branch2]"


# r8 — red [branch1]
git checkout branch1
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r8/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 8 (r8)"
echo "- Коммит r8 (red) [branch1]"


# r9 — blue [branch2] change in Revision r9(cuz files in r7 and r9 are same)
git checkout branch2
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r9/* src/ 2>/dev/null || true
git add -A .
git commit --allow-empty --author="blue <blue@example.com>" -m "Revision 9 (r9)"
echo "- Коммит r9 (blue) [branch2]"


# r10 — red [branch1]
git checkout branch1
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r10/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 10 (r10)"
echo "- Коммит r10 (red) [branch1]"


# r11 — blue [branch2]
git checkout branch2
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r11/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 11 (r11)"
echo "- Коммит r11 (blue) [branch2]"


# r12 — blue [branch2]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r12/* src/ 2>/dev/null || true
git add -A .
git commit --author="blue <blue@example.com>" -m "Revision 12 (r12)"
echo "- Коммит r12 (blue) [branch2]"


# СЛИЯНИЕ branch2 -> branch1  =>  r13 (red)
git checkout branch1
git merge --no-commit branch2 -Xtheirs
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r13/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 13 (r13)"
echo "- Коммит r13 (red) [merge branch2 -> branch1]"


# r14 — red [branch1]
mkdir -p src
rm -rf src/* 2>/dev/null || true
cp -r rs/r14/* src/ 2>/dev/null || true
git add -A .
git commit -m "Revision 14 (r14)"
echo "- Коммит r14 (red) [branch1]"


echo ""
echo "====== ГРАФ КОММИТОВ ======"
git log \
    --graph \
    --abbrev-commit \
    --decorate \
    --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(auto)%d%C(reset)' \
    --all