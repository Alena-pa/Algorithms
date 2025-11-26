#include <iostream>
#include <iomanip>
#include <vector>
#include <math.h>
#include <set>
#include <random>
#include <chrono>
using namespace std;

vector<long long> random_vector(int n, long long max_val) {
    mt19937 rng(random_device{}());
    uniform_int_distribution<long long> dist(0, max_val);
    vector<long long> v(n);
    for (auto& x : v) x = dist(rng);
    return v;
}

vector<long long> generate_smooth(int n) {
    set<long long> numbers = { 1 };
    vector<long long> res;

    while (!numbers.empty()) {
        long long cur = *numbers.begin();
        numbers.erase(numbers.begin());

        if (cur >= n) break;
        res.push_back(cur);

        numbers.insert(cur * 2);
        numbers.insert(cur * 3);
    }

    return res;
}

void shell_sort_custom(vector<long long>& v) {
    int n = v.size();
    auto gaps = generate_smooth(n / 3);

    for (auto it = gaps.rbegin(); it != gaps.rend(); ++it) {
        int h = *it;
        for (int i = h; i < n; ++i) {
            long long temp = v[i];
            int j = i;
            while (j >= h && v[j - h] > temp) {
                v[j] = v[j - h];
                j -= h;
            }
            v[j] = temp;
        }
    }
}

void test(vector<long long>& v, void (*sort_func)(vector<long long>&)) {
    vector<long long> vec_std = v;

    auto start_std = chrono::steady_clock::now();
    sort(vec_std.begin(), vec_std.end());
    auto end_std = chrono::steady_clock::now();
    chrono::duration<double> elapsed_std = end_std - start_std;
    cout << "std::sort time: " << elapsed_std.count() << " s\n";

    auto start_custom = chrono::steady_clock::now();
    sort_func(v);
    auto end_custom = chrono::steady_clock::now();
    chrono::duration<double> elapsed_custom = end_custom - start_custom;
    cout << "Shell sort time: " << elapsed_custom.count() << " s\n";

    if (elapsed_std < elapsed_custom) {
        double speedup = elapsed_custom.count() / elapsed_std.count();
        cout << "std::sort is " << speedup << "x faster\n";
    }
    else {
        double speedup = elapsed_std.count() / elapsed_custom.count();
        cout << "Shell sort is " << speedup << "x faster\n";
    }
}

void test_generator(const vector<int>& sizes) {
    for (int pow10 : sizes) {
        long long n = pow(10, pow10);
        cout << "\nTEST FOR N = 10^" << pow10 << " (" << n << " elements)\n";

        auto vec = random_vector(n, 1e8);
        test(vec, shell_sort_custom);

        cout << "--------------------------\n";
    }
}

int main() {
    vector<int> test_sizes = { 3, 4, 5, 6 };
    test_generator(test_sizes);
}