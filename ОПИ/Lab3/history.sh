#!/usr/bin/env bash
# =============================================================
# history.sh — поиск последней рабочей git-ревизии
#
# Используется Ant-целью "history".
# Алгоритм:
#   1. Получить список всех коммитов (от HEAD до самого первого)
#   2. Для каждой ревизии:
#      a. git checkout <rev>
#      b. Попытка javac
#      c. Если компиляция успешна — сохранить rev как LAST_WORKING
#         и выйти из цикла
#   3. Если LAST_WORKING найден:
#      - Найти NEXT_REV (ревизия, сразу следующая за LAST_WORKING)
#      - git diff LAST_WORKING NEXT_REV > broken_diff_<timestamp>.diff
#   4. git checkout HEAD (вернуться на последний коммит)
#   5. Вывести итоговый отчёт
# =============================================================

set -euo pipefail

SRC_DIR="${1:-src/main/java}"
CLASSES_DIR="${2:-build/classes}"
LIB_DIR="${3:-lib/compile}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DIFF_FILE="broken_diff_${TIMESTAMP}.diff"

echo "========================================================"
echo " [history] Начало поиска последней рабочей ревизии"
echo " SRC_DIR    = $SRC_DIR"
echo " CLASSES_DIR= $CLASSES_DIR"
echo " LIB_DIR    = $LIB_DIR"
echo "========================================================"

# Проверяем, что мы в git-репозитории
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "[history] ОШИБКА: Текущая директория не является git-репозиторием!"
    exit 1
fi

# Запоминаем текущую ветку/ревизию для возврата в конце
ORIGINAL_REV=$(git rev-parse HEAD)
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "[history] Текущая ревизия: $ORIGINAL_REV (ветка: $ORIGINAL_BRANCH)"

# Получаем список всех хешей коммитов (от нового к старому)
# Пропускаем HEAD (он уже проверен в Ant и не компилируется)
mapfile -t ALL_REVS < <(git log --format="%H" HEAD)

TOTAL=${#ALL_REVS[@]}
echo "[history] Найдено ревизий в истории: $TOTAL"

if [ "$TOTAL" -eq 0 ]; then
    echo "[history] История пуста. Нечего откатывать."
    exit 1
fi

LAST_WORKING=""
LAST_WORKING_INDEX=-1

# Собираем classpath из lib/compile
CLASSPATH_STR=""
if [ -d "$LIB_DIR" ]; then
    for jar in "$LIB_DIR"/*.jar; do
        [ -f "$jar" ] && CLASSPATH_STR="$CLASSPATH_STR:$jar"
    done
fi
# Убираем ведущее двоеточие
CLASSPATH_STR="${CLASSPATH_STR#:}"

echo "[history] Classpath: $CLASSPATH_STR"
echo "--------------------------------------------------------"

# Функция компиляции текущего checkout
try_compile() {
    local dest="$1"
    rm -rf "$dest"
    mkdir -p "$dest"

    # Собираем все .java файлы
    local java_files
    java_files=$(find "$SRC_DIR" -name "*.java" 2>/dev/null | tr '\n' ' ')

    if [ -z "$java_files" ]; then
        echo "  [try_compile] Нет .java файлов в $SRC_DIR"
        return 1
    fi

    if [ -n "$CLASSPATH_STR" ]; then
        # shellcheck disable=SC2086
        javac -cp "$CLASSPATH_STR" \
              -d "$dest" \
              -encoding UTF-8 \
              --release 17 \
              $java_files 2>/dev/null
    else
        # shellcheck disable=SC2086
        javac -d "$dest" \
              -encoding UTF-8 \
              --release 17 \
              $java_files 2>/dev/null
    fi
}

# Основной цикл: перебираем ревизии начиная с предпоследней (индекс 1)
for i in "${!ALL_REVS[@]}"; do
    # Пропускаем HEAD (уже известно, что не компилируется)
    [ "$i" -eq 0 ] && continue

    REV="${ALL_REVS[$i]}"
    REV_SHORT="${REV:0:8}"
    MSG=$(git log --format="%s" -1 "$REV" 2>/dev/null || echo "???")

    echo "[history] [$((i))/$((TOTAL-1))] Проверяем ревизию: $REV_SHORT  \"$MSG\""

    # Checkout ревизии (detached HEAD)
    git checkout --quiet "$REV" 2>/dev/null

    # Попытка компиляции
    if try_compile "${CLASSES_DIR}_history_test"; then
        echo "[history] ✓ Ревизия $REV_SHORT компилируется успешно!"
        LAST_WORKING="$REV"
        LAST_WORKING_INDEX="$i"
        break
    else
        echo "[history] ✗ Ревизия $REV_SHORT не компилируется, откатываемся дальше..."
    fi
done

# Очищаем временную папку теста
rm -rf "${CLASSES_DIR}_history_test"

echo "--------------------------------------------------------"

# Возвращаемся на исходную ветку
git checkout --quiet "$ORIGINAL_REV" 2>/dev/null || true
if [ "$ORIGINAL_BRANCH" != "HEAD" ]; then
    git checkout --quiet "$ORIGINAL_BRANCH" 2>/dev/null || true
fi
echo "[history] Возвращены на исходную ревизию: $ORIGINAL_BRANCH"

# Анализ результатов
if [ -z "$LAST_WORKING" ]; then
    echo ""
    echo "========================================================" 
    echo " [history] РЕЗУЛЬТАТ: Ни одна ревизия не компилируется!"
    echo " Даже самая первая ревизия содержит ошибки компиляции."
    echo "========================================================"
    exit 2
fi

# Ревизия, сразу следующая за LAST_WORKING (т.е. та, что сломала сборку)
NEXT_INDEX=$((LAST_WORKING_INDEX - 1))
if [ "$NEXT_INDEX" -ge 0 ]; then
    NEXT_WORKING="${ALL_REVS[$NEXT_INDEX]}"
    NEXT_SHORT="${NEXT_WORKING:0:8}"
    NEXT_MSG=$(git log --format="%s" -1 "$NEXT_WORKING" 2>/dev/null || echo "???")
else
    # Следующая — это HEAD
    NEXT_WORKING="$ORIGINAL_REV"
    NEXT_SHORT="${ORIGINAL_REV:0:8}"
    NEXT_MSG=$(git log --format="%s" -1 "$NEXT_WORKING" 2>/dev/null || echo "???")
fi

echo ""
echo "========================================================"
echo " [history] РЕЗУЛЬТАТ:"
echo "   Последняя рабочая ревизия : ${LAST_WORKING:0:8}"
echo "   Ревизия, сломавшая сборку : $NEXT_SHORT  \"$NEXT_MSG\""
echo "========================================================"

# Генерируем diff между рабочей и следующей ревизией
echo "[history] Генерация diff-файла: $DIFF_FILE"
{
    echo "# Diff: последняя рабочая ревизия → ревизия, сломавшая сборку"
    echo "# Рабочая : $LAST_WORKING"
    echo "# Сломанная: $NEXT_WORKING  ($NEXT_MSG)"
    echo "# Дата: $(date)"
    echo "# ================================================================"
    git diff "$LAST_WORKING" "$NEXT_WORKING"
} > "$DIFF_FILE"

echo "[history] Diff записан в: $DIFF_FILE"
echo ""
echo "[history] Совет: Изучите $DIFF_FILE, чтобы найти ошибку."
echo "          Для отката к рабочей ревизии выполните:"
echo "          git checkout ${LAST_WORKING:0:8}"
echo "========================================================"

exit 0