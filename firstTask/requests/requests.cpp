#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
using namespace std;

vector<int> generate_random_array(int array_size, int value_range, mt19937& gen) {
    uniform_int_distribution<int> distrib(0, value_range - 1);
    vector<int> arr(array_size);
    for (int i = 0; i < array_size; ++i) {
        arr[i] = distrib(gen);
    }
    return arr;
}

vector<int> build_frequency_table(const vector<int>& arr, int value_range) {
    vector<int> frequency(value_range, 0);
    for (int number : arr) {
        frequency[number]++;
    }
    return frequency;
}

vector<int> build_prefix_sum(const vector<int>& frequency) {
    vector<int> prefix_sum(frequency.size() + 1, 0);
    for (size_t i = 1; i <= frequency.size(); ++i) {
        prefix_sum[i] = prefix_sum[i - 1] + frequency[i - 1];
    }
    return prefix_sum;
}

int answer_query(int left_bound, int right_bound, const vector<int>& prefix_sum, int value_range) {
    left_bound = max(left_bound, 0);
    right_bound = min(right_bound, value_range - 1);
    if (left_bound > right_bound) {
        return 0;
    }
    return prefix_sum[right_bound + 1] - prefix_sum[left_bound];
}

int main() {
    cout << "Enter array size N and value range K: ";
    int array_size, value_range;
    cin >> array_size >> value_range;

    random_device rd;
    mt19937 gen(rd());
    vector<int> array = generate_random_array(array_size, value_range, gen);

    if (array_size <= 100) {
        cout << "Generated array: ";
        for (int x : array) {
            cout << x << " ";
        }
        cout << "\n";
    }
    else {
        cout << "Generated array of size " << array_size << " (too large to display).\n";
    }

    vector<int> frequency = build_frequency_table(array, value_range);
    vector<int> prefix_sum = build_prefix_sum(frequency);

    cout << "Enter the number of queries: ";
    int query_count;
    cin >> query_count;

    cout << "Processing queries:\n";
    for (int i = 0; i < query_count; ++i) {
        int left_bound, right_bound;
        cout << "Query " << i + 1 << ": enter segment boundaries [l, r]: ";
        cin >> left_bound >> right_bound;

        int result = answer_query(left_bound, right_bound, prefix_sum, value_range);
        cout << "Answer: " << result << "\n";
    }

    return 0;
}