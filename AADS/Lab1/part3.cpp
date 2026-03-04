#include <cctype>
#include <iostream>
#include <map>
#include <queue>
#include <stack>
#include <string>

using namespace std;

pair<string, string> split_assignment(const string &input)
{
    size_t equal_pos = input.find('=');
    return {input.substr(0, equal_pos), input.substr(equal_pos + 1)};
}

inline bool check_is_number(const string &str)
{
    return !str.empty() && (isdigit(str[0]) || str[0] == '-');
}

long long fetch_var_value(const map<string, stack<long long>> &var_map,
                          const string &name)
{
    auto iter = var_map.find(name);
    if (iter == var_map.end() || iter->second.empty())
    {
        return 0LL;
    }
    return iter->second.top();
}

inline void revert_scope(map<string, stack<long long>> &var_map,
                         stack<queue<string>> &level_mods)
{
    while (!level_mods.top().empty())
    {
        var_map[level_mods.top().front()].pop();
        level_mods.top().pop();
    }
    level_mods.pop();
}

int main()
{
    cin.tie(nullptr);

    map<string, stack<long long>> var_map;
    stack<queue<string>> level_mods;
    level_mods.emplace();

    string input_str;
    while (getline(cin, input_str))
    {
        if (input_str == "{")
        {
            level_mods.emplace();
        }
        else if (input_str == "}")
        {
            revert_scope(var_map, level_mods);
        }
        else
        {
            auto [left_var, right_part] = split_assignment(input_str);
            long long assign_val;
            if (check_is_number(right_part))
            {
                assign_val = stoll(right_part);
            }
            else
            {
                assign_val = fetch_var_value(var_map, right_part);
                cout << assign_val << endl;
            }
            level_mods.top().push(left_var);
            var_map[left_var].push(assign_val);
        }
    }
    return 0;
}