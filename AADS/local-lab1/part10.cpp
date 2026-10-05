#include <deque>
#include <iostream>

class MiddleInsertQueue {
private:
  std::deque<int> left;
  std::deque<int> right;

  void rebalance() {
    if (left.size() < right.size()) {
      left.push_back(right.front());
      right.pop_front();
    } else if (left.size() > right.size() + 1) {
      right.push_front(left.back());
      left.pop_back();
    }
  }

public:
  void push_back(int val) {
    right.push_back(val);
    rebalance();
  }

  void push_middle(int val) {
    right.push_front(val);
    rebalance();
  }

  int pop_front() {
    int val = left.front();
    left.pop_front();
    rebalance();
    return val;
  }
};

int main() {
  std::ios_base::sync_with_stdio(false);
  std::cin.tie(nullptr);

  int n;
  if (!(std::cin >> n))
    return 0;

  MiddleInsertQueue q;

  while (n--) {
    char op;
    std::cin >> op;
    if (op == '+') {
      int val;
      std::cin >> val;
      q.push_back(val);
    } else if (op == '*') {
      int val;
      std::cin >> val;
      q.push_middle(val);
    } else if (op == '-') {
      std::cout << q.pop_front() << "\n";
    }
  }

  return 0;
}