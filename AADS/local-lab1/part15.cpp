#include <bits/stdc++.h>
using namespace std;

const int MAXN = 205;
int parent[MAXN];

int find_way_cheated(int x) {
  return parent[x] == x ? x : parent[x] = find_way_cheated(parent[x]);
}

void is_cheated_together(int x, int y) {
  x = find_way_cheated(x);
  y = find_way_cheated(y);
  if (x != y)
    parent[x] = y;
}

int main() {
  int N, M;
  cin >> N >> M;

  for (int i = 0; i < 2 * N; i++) {
    parent[i] = i;
  }

  bool possible = true;

  for (int i = 0; i < M; i++) {
    int u, v;
    cin >> u >> v;
    u--;
    v--;

    if (find_way_cheated(u) == find_way_cheated(v)) {
      possible = false;
    }

    is_cheated_together(u, v + N);
    is_cheated_together(v, u + N);
  }

  cout << (possible ? "YES" : "NO") << endl;
  return 0;
}