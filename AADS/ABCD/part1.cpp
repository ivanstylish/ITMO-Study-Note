#include <bits/stdc++.h>

using namespace std;

int main() {
  int n;
  std::cin >> n;

  vector<int> raised_flo_bed(n); // 设置动态数组，模拟花坛中的花朵
  for (int i = 0; i < n; ++i) {
    cin >> raised_flo_bed[i];
  }
  int flower_start = 1;
  int flower_end = 1;
  int max_length = 1;
  int cur_length;
  int cur_start = 1;
  int count = 1;
  int pre_value = raised_flo_bed[0];

  for (int i = 1; i < n; ++i) { // 0-based i，从1到n-1，避免越界
    if (raised_flo_bed[i] == pre_value) {
      ++count;
    } else {
      count = 1;
    }
    pre_value = raised_flo_bed[i];

    if (count >= 3) {
      cur_start = i; // 重置到第二个相同的位置（1-based: i，因为i 0-based, 1-based = i）
      count = 2; // 保留两个相同，不能有3个一样的
    }

    cur_length = (i + 1) - cur_start + 1; // i+1是当前1-based位置
    if (cur_length > max_length) {
      flower_start = cur_start;
      flower_end = i + 1;
      max_length = cur_length;
    }
  }

  cout << flower_start << " " << flower_end << endl;

  return 0;
}