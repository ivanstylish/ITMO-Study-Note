#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  int N, K, P;
  cin >> N >> K >> P;

  vector<int> seq(P);
  for (int i = 0; i < P; i++) {
    cin >> seq[i];
    seq[i]--;
  }

  vector<int> next_use(P);
  vector<int> last_pos(N, P);
  for (int i = P - 1; i >= 0; i--) {
    next_use[i] = last_pos[seq[i]];
    last_pos[seq[i]] = i;
  }

  unordered_map<int, int> on_floor;
  set<pair<int, int>> ordered;

  int operations = 0;

  for (int i = 0; i < P; i++) {
    int toy = seq[i];

    if (on_floor.count(toy)) {
      int old_next = on_floor[toy];
      ordered.erase({old_next, toy});
      on_floor[toy] = next_use[i];
      ordered.insert({next_use[i], toy});
    } else {
      operations++;

      if ((int)on_floor.size() == K) {
        auto it = prev(ordered.end());
        int evict_toy = it->second;
        ordered.erase(it);
        on_floor.erase(evict_toy);
      }

      on_floor[toy] = next_use[i];
      ordered.insert({next_use[i], toy});
    }
  }

  cout << operations << "\n";
  return 0;
}