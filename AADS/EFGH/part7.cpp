#include <algorithm>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  string s;
  cin >> s;

  long long w[26];
  for (int i = 0; i < 26; i++) {
    cin >> w[i];
  }

  int cnt[26] = {};
  for (char c : s) {
    cnt[c - 'a']++;
  }

  int n = s.size();

  vector<int> order;
  for (int i = 0; i < 26; i++) {
    if (cnt[i] >= 2) {
      order.push_back(i);
    }
  }
  sort(order.begin(), order.end(), [&](int a, int b) { return w[a] > w[b]; });

  string result(n, ' ');
  int left = 0, right = n - 1;
  bool used[26] = {};

  for (int idx : order) {
    if (left >= right) {
      break;
    }
    result[left++] = 'a' + idx;
    result[right--] = 'a' + idx;
    cnt[idx] -= 2;
    used[idx] = true;
  }

  int mid = left;
  for (int i = 0; i < 26; i++) {
    for (int j = 0; j < cnt[i]; j++) {
      result[mid++] = 'a' + i;
    }
  }

  cout << result << endl;
  return 0;
}