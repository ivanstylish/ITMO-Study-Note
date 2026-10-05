#include <bits/stdc++.h>
using namespace std;
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int N, K;
  cin >> N >> K;
  vector<int> a(N);
  vector<int> pre(N), suf(N);
  for (auto& x : a) {
    cin >> x;
  }
  for (int i = 0; i < N; i++) {
    if (i % K == 0) {
      pre[i] = a[i];
    } else {
      pre[i] = min(pre[i - 1], a[i]);
    }
  }
  for (int i = N - 1; i >= 0; i--) {
    if (i % K == K - 1 || i == N - 1) {
      suf[i] = a[i];
    } else {
      suf[i] = min(suf[i + 1], a[i]);
    }
  }
  for (int i = 0; i <= N - K; i++) {
    cout << min(suf[i], pre[i + K - 1]) << (i == N - K ? "" : " ");
  }
  cout << endl;
}