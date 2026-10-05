#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  int N, M, sx, sy, ex, ey;
  cin >> N >> M >> sx >> sy >> ex >> ey;
  sx--;
  sy--;
  ex--;
  ey--;

  vector<string> grid(N);
  for (auto& row : grid)
    cin >> row;

  auto h = [&](int x, int y) { return abs(x - ex) + abs(y - ey); };

  vector<vector<int>> g(N, vector<int>(M, INT_MAX));
  vector<vector<char>> pdir(N, vector<char>(M, 0));

  priority_queue<tuple<int, int, int, int>, vector<tuple<int, int, int, int>>, greater<>> open;
  g[sx][sy] = 0;
  open.push({h(sx, sy), 0, sx, sy});

  int dx[] = {-1, 0, 1, 0};
  int dy[] = {0, 1, 0, -1};
  char dirs[] = {'N', 'E', 'S', 'W'};

  while (!open.empty()) {
    auto [f, gv, x, y] = open.top();
    open.pop();
    if (gv > g[x][y])
      continue;
    if (x == ex && y == ey)
      break;

    for (int i = 0; i < 4; i++) {
      int nx = x + dx[i], ny = y + dy[i];
      if (nx < 0 || nx >= N || ny < 0 || ny >= M)
        continue;
      char c = grid[nx][ny];
      if (c == '#')
        continue;
      int cost = (c == '.') ? 1 : 2;
      int ng = gv + cost;
      if (ng < g[nx][ny]) {
        g[nx][ny] = ng;
        pdir[nx][ny] = dirs[i];
        open.push({ng + h(nx, ny), ng, nx, ny});
      }
    }
  }

  if (g[ex][ey] == INT_MAX) {
    cout << -1;
    return 0;
  }

  string path;
  int cx = ex, cy = ey;
  while (cx != sx || cy != sy) {
    char d = pdir[cx][cy];
    path += d;
    if (d == 'N')
      cx++;
    else if (d == 'S')
      cx--;
    else if (d == 'E')
      cy--;
    else
      cy++;
  }
  reverse(path.begin(), path.end());
  cout << g[ex][ey] << "\n" << path << "\n";
}