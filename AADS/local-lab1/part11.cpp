#include <iostream>
#include <set>
#include <vector>

using namespace std;

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(NULL);

  long long n, m;
  if (!(cin >> n >> m))
    return 0;
  set<pair<long long, long long>> pos_map;
  set<pair<long long, long long>> len_map;

  pos_map.insert({1, n});
  len_map.insert({n, 1});

  vector<pair<long long, long long>> history(m + 1, {-1, 0});

  for (int i = 1; i <= m; ++i) {
    long long q;
    cin >> q;

    if (q > 0) {
      auto it = len_map.lower_bound({q, -1});

      if (it == len_map.end()) {
        cout << "-1\n";
      } else {
        long long length = it->first;
        long long start = it->second;

        len_map.erase(it);
        pos_map.erase({start, start + length - 1});

        cout << start << "\n";
        history[i] = {start, q};

        if (length > q) {
          long long new_start = start + q;
          long long new_len = length - q;
          len_map.insert({new_len, new_start});
          pos_map.insert({new_start, new_start + new_len - 1});
        }
      }
    } else {
      int id = (int)(-q);
      if (history[id].first == -1)
        continue;

      long long curL = history[id].first;
      long long curR = curL + history[id].second - 1;

      auto nxt = pos_map.lower_bound({curR + 1, -1});
      if (nxt != pos_map.end() && nxt->first == curR + 1) {
        long long nxtL = nxt->first;
        long long nxtR = nxt->second;
        len_map.erase({nxtR - nxtL + 1, nxtL});
        curR = nxtR;
        pos_map.erase(nxt);
      }

      auto prv = pos_map.lower_bound({curL, -1});
      if (prv != pos_map.begin()) {
        --prv;
        if (prv->second == curL - 1) {
          long long prvL = prv->first;
          long long prvR = prv->second;
          len_map.erase({prvR - prvL + 1, prvL});
          curL = prvL;
          pos_map.erase(prv);
        }
      }

      pos_map.insert({curL, curR});
      len_map.insert({curR - curL + 1, curL});
    }
  }
  return 0;
}