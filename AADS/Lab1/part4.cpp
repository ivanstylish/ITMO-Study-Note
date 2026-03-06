#include <bits/stdc++.h>
using namespace std;

int main() {
  long a, k = -1;
  long last_value = -1;
  uint16_t b, c, d;
  cin >> a >> b >> c >> d >> k;

  do {
    if (k-- == 0) {
      break;
    }
    long temp_value = a * b - c;
    if (temp_value > d) {
      temp_value = d;
    }
    if (temp_value <= 0) {
      a = 0;
      break;
    }
    if (temp_value == last_value) {
      break;
    }
    last_value = a;
    a = temp_value;
  } while (true);

  cout << a << endl;
}