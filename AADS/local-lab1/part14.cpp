#include <iostream>
#include <vector>

using namespace std;

int find_set(int v, vector<int>& p) {
  if (v == p[v])
    return v;
  return p[v] = find_set(p[v], p);
}

int main() {
  int n;
  cin >> n;

  vector<int> p(n + 1);
  vector<int> rk(n + 1, 0);
  for (int i = 1; i <= n; ++i)
    p[i] = i;

  int ans = 0;
  for (int i = 1; i <= n; ++i) {
    int target;
    cin >> target;
    int a = find_set(i, p);
    int b = find_set(target, p);

    if (a != b) {
      if (rk[a] < rk[b])
        swap(a, b);
      p[b] = a;
      if (rk[a] == rk[b])
        rk[a]++;
    } else {
      ans++;
    }
  }
  cout << ans << "\n";
  return 0;
}