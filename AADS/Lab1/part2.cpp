#include <bits/stdc++.h>

using namespace std;

bool different_cases(char a, char b) {
  return toupper(a) == toupper(b) && a != b;
}

int main() {
  string input;
  if (!(cin >> input)) {
    return 0;
  }
  int n = input.length();
  if (n % 2 != 0) {
    cout << "Impossible" << endl;
    return 0;
  }
  stack<char> pos;
  stack<int> animals;
  stack<int> traps;

  vector<int> trap_to_animal(n, 0);

  int animal_count = 0;
  for (int i = 0; i < n; i++) {
    char cur_char = input[i];

    if (isupper(cur_char)) {
      traps.push(i);
    } else {
      ++animal_count;
      animals.push(animal_count);
    }

    if (pos.empty() || !different_cases(cur_char, pos.top())) {
      pos.push(cur_char);
    } else {
      int trap_index = traps.top();
      trap_to_animal[trap_index] = animals.top();

      animals.pop();
      traps.pop();
      pos.pop();
    }
  }

  if (!pos.empty()) {
    cout << "Impossible" << endl;
    return 0;
  }

  cout << "Possible\n";
  bool first = true;
  for (int i = 0; i < n; i++) {
    if (isupper(input[i])) {
      if (!first)
        cout << " ";
      cout << trap_to_animal[i];
      first = false;
    }
  }
  cout << endl;

  return 0;
}