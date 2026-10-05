#include <bits/stdc++.h>
using namespace std;

bool is_strongly_connected(int n, int limit, const vector<vector<int>>& adj_matrix) {
  vector<vector<int>> forward(n), backward(n);
  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      if (i != j && adj_matrix[i][j] <= limit) {
        forward[i].push_back(j);
        backward[j].push_back(i);
      }
    }
  }

  auto check = [&](const vector<vector<int>>& g) {
    vector<bool> flewby(n, false);
    queue<int> q;
    q.push(0);
    flewby[0] = true;
    int count = 1;
    while (!q.empty()) {
      int u = q.front();
      q.pop();
      for (int v : g[u]) {
        if (!flewby[v]) {
          flewby[v] = true;
          count++;
          q.push(v);
        }
      }
    }
    return count == n;
  };

  return check(forward) && check(backward);
}

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  int n;
  if (!(cin >> n))
    return 0;
  if (n <= 1) {
    cout << 0 << endl;
    return 0;
  }

  vector<vector<int>> adj(n, vector<int>(n));
  vector<int> weights;

  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      cin >> adj[i][j];
      if (i != j)
        weights.push_back(adj[i][j]);
    }
  }

  sort(weights.begin(), weights.end());
  weights.erase(unique(weights.begin(), weights.end()), weights.end());

  int low = 0, high = weights.size() - 1;
  int ans = weights.back();

  while (low <= high) {
    int mid = low + (high - low) / 2;
    if (is_strongly_connected(n, weights[mid], adj)) {
      ans = weights[mid];
      high = mid - 1;
    } else {
      low = mid + 1;
    }
  }

  cout << ans << endl;
  return 0;
}