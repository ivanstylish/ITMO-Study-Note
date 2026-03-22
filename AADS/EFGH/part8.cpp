#include <cstdio>

using namespace std;

inline void read(int& num) {
  num = 0;
  char ch = getchar();
  while (ch < '0' || ch > '9') {
    ch = getchar();
  }
  while (ch >= '0' && ch <= '9') {
    num = (num << 3) + (num << 1) + (ch ^ 48);
    ch = getchar();
  }
}

void heapify(int arr[], int n, int i) {
  int largest = i;
  int l = 2 * i + 1;
  int r = 2 * i + 2;
  if (l < n && arr[l] > arr[largest]) {
    largest = l;
  }
  if (r < n && arr[r] > arr[largest]) {
    largest = r;
  }
  if (largest != i) {
    int tmp = arr[i];
    arr[i] = arr[largest];
    arr[largest] = tmp;
    heapify(arr, n, largest);
  }
}

void heapSort(int arr[], int n) {
  for (int i = n / 2 - 1; i >= 0; i--) {
    heapify(arr, n, i);
  }
  for (int i = n - 1; i > 0; i--) {
    int tmp = arr[0];
    arr[0] = arr[i];
    arr[i] = tmp;
    heapify(arr, i, 0);
  }
}

int main() {
  int n, k;
  int prices[100001];
  long long sum = 0;

  read(n);
  read(k);

  for (int i = 0; i < n; i++) {
    read(prices[i]);
  }

  heapSort(prices, n);

  for (int i = n - 1; i >= 0; i--) {
    int pos = n - i;
    if (pos % k != 0) {
      sum += prices[i];
    }
  }

  printf("%lld", sum);

  return 0;
}