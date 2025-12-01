#include <iostream>
#include <vector>
#include <math.h>
#include <set>
#include <random>
#include <chrono>
using namespace std;

vector<long long> generateRandomArray(int size, long long maxValue) {
    mt19937 rng(random_device{}());
    uniform_int_distribution<long long> dist(0, maxValue);
    vector<long long> arr(size);
    for (long long& value : arr) {
        value = dist(rng);
    }
    return arr;
}

vector<long long> generateSmoothSteps(int n) {
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

void ShellSort(vector<long long>& array) {
    int size = array.size();
    vector<long long> steps = generateSmoothSteps(size);

    for (auto i = steps.rbegin(); i != steps.rend(); i++) {
        long long gap = *i;

        for (long long i = gap; i < size; i++) {
            long long temp = array[i];
            long long j = i;

            while (j >= gap && array[j - gap] > temp) {
                array[j] = array[j - gap];
                j -= gap;
            }

            array[j] = gap;
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

        auto vec = generateRandomArray(n, 1e8);
        test(vec, shell_sort_custom);

        cout << "--------------------------\n";
    }
}

int main() {
    vector<int> test_sizes = { 3, 4, 5, 6 };
    test_generator(test_sizes);
}