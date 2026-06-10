#!/bin/bash
export PATH="/c/Program Files/TortoiseSVN/bin:$PATH"

# --- Создание репозитория ---
svnadmin create repo
REPO_URL="file:///D:/Undergraduate/Sophomore/FOSE/lab2/repo"
echo "- Репозиторий создан: $REPO_URL"

svn mkdir -m "project structure" $REPO_URL/trunk $REPO_URL/branches
echo "- trunk/branches созданы"

# --- Рабочая копия ---
svn checkout $REPO_URL/trunk/ wc
cd wc

# Вспомогательная функция для чистого обновления файлов (без svn rm *)
# Удаляет всё, кроме скрытой папки .svn, затем копирует новые файлы
update_src() {
    # Удаляем все файлы и папки, кроме .svn
    find . -maxdepth 1 ! -name '.' ! -name '.svn' -exec rm -rf {} +
    # Копируем файлы новой ревизии
    cp -r ../rs/$1/* . 2>/dev/null || true
    # Рекурсивно добавляем все новые файлы (существующие изменятся автоматически)
    svn add * --force 2>/dev/null || true
}

# r0 — red [trunk]
update_src "r0"
svn commit -m "Initial commit (r0)" --username=red
echo "- Коммит r0 (red) [trunk]"

# r1 — blue [trunk]
update_src "r1"
svn commit -m "Revision 1 (r1)" --username=blue
echo "- Коммит r1 (blue) [trunk]"

# r3 — blue: создание branch2 от trunk(r1), коммит на branch2
svn copy $REPO_URL/trunk $REPO_URL/branches/branch2 -m "Creating branch2 (r3)"
svn switch $REPO_URL/branches/branch2
update_src "r3"
svn commit -m "Revision 3 (r3)" --username=blue
echo "- Коммит r3 (blue) [branch2 от r1]"

# r2 — red [trunk]
svn switch $REPO_URL/trunk
svn update
update_src "r2"
svn commit -m "Revision 2 (r2)" --username=red
echo "- Коммит r2 (red) [trunk]"

# r4 — red [trunk]
update_src "r4"
svn commit -m "Revision 4 (r4)" --username=red
echo "- Коммит r4 (red) [trunk]"

# r5 — red [branch2]
svn switch $REPO_URL/branches/branch2
update_src "r5"
svn commit -m "Revision 5 (r5)" --username=red
echo "- Коммит r5 (red) [branch2]"

# r6 — red [branch2]
update_src "r6"
svn commit -m "Revision 6 (r6)" --username=red
echo "- Коммит r6 (red) [branch2]"

# r7 — red [branch2]
update_src "r7"
svn commit -m "Revision 7 (r7)" --username=red
echo "- Коммит r7 (red) [branch2]"

# r8 — red [trunk]
svn switch $REPO_URL/trunk
svn update
update_src "r8"
svn commit -m "Revision 8 (r8)" --username=red
echo "- Коммит r8 (red) [trunk]"

# r9 — blue [branch2]
svn switch $REPO_URL/branches/branch2
svn update
update_src "r9"
svn commit -m "Revision 9 (r9)" --username=blue
echo "- Коммит r9 (blue) [branch2]"

# r10 — red [trunk]
svn switch $REPO_URL/trunk
svn update
update_src "r10"
svn commit -m "Revision 10 (r10)" --username=red
echo "- Коммит r10 (red) [trunk]"

# r11 — blue [branch2]
svn switch $REPO_URL/branches/branch2
update_src "r11"
svn commit -m "Revision 11 (r11)" --username=blue
echo "- Коммит r11 (blue) [branch2]"

# r12 — blue [branch2]
update_src "r12"
svn commit -m "Revision 12 (r12)" --username=blue
echo "- Коммит r12 (blue) [branch2]"

# СЛИЯНИЕ branch2 -> trunk  =>  r13 (red)
svn switch $REPO_URL/trunk
svn update

# Выполняем слияние
svn merge $REPO_URL/branches/branch2

# РАЗРЕШЕНИЕ КОНФЛИКТОВ 
# Если в файле были изменения и в trunk, и в branch2, возникнет конфликт (Conflict).
# SVN создаст файлы .mine, .r10, .r12 и вставит маркеры <<<<<<< в сам файл.
# Привести файлы к эталонному состоянию варианта (rs/r13),
# а затем сообщить SVN, что конфликт разрешен.
update_src "r13"

# Находим все файлы, находящиеся в состоянии конфликта, и помечаем их как разрешенные
svn status | grep '^C' | awk '{print $2}' | while read fname; do
    svn resolve --accept working "$fname"
    echo "- Конфликт в файле $fname разрешен (принята рабочая копия r13)"
done

svn commit -m "Revision 13 (r13)" --username=red
echo "- Коммит r13 (red) [merge branch2 -> trunk]"

# r14 — red [trunk]
update_src "r14"
svn commit -m "Revision 14 (r14)" --username=red
echo "- Коммит r14 (red) [trunk]"

svn update

echo ""
echo "====== ИСТОРИЯ РЕВИЗИЙ SVN ======"
svn log $REPO_URL --verbose