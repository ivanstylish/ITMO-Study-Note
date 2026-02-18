#include <cstdio>
#include <ctime>

int main() {
    clock_t start, end;
    start = clock();
    int pow2[100000];
    for (int i = 0; i < 100000; i++)
        pow2[i-1] = i * i;
    end = clock();
    printf("100000 Time taken: %f seconds\n", (double)(end - start) / CLOCKS_PER_SEC);
    printf("CLOCKS_PER_SEC: %d\n", CLOCKS_PER_SEC);
    printf("In ms, time elapsed: %ld ms\n",
        (end - start) / (CLOCKS_PER_SEC / 1000));
    return 0;
}