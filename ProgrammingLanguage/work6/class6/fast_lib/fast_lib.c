/ Это библиотека, а не исполняемый файл,
// поэтому функция main() и stdio.h не требуются (кроме бонуса).

// Макрос для экспорта функций (dllexport для Windows, по умолчанию для POSIX)
#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
#include "pch.h"

// Важно: используется 'long long' для предотвращения переполнения
DLLEXPORT long long fib_c(int n) {
    if (n <= 1) {
        return n;
    }
    else {
        return fib_c(n - 1) + fib_c(n - 2);
    }
}

// Оптимальная итеративная версия для демонстрации
DLLEXPORT long long fib_c_iterative(int n) {
    if (n <= 1) return n;

    long long a = 0;
    long long b = 1;
    long long temp;

    for (int i = 2; i <= n; i++) {
        temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}