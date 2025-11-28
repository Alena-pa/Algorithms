#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <chrono>

using namespace std;

void countSort(vector<string>& arr, int pos) {
    int n = arr.size();
    vector<string> output(n);
    int count[27] = { 0 };

    for (int i = 0; i < n; i++) {
        int index = (pos >= arr[i].size()) ? 0 : arr[i][pos] - 'a' + 1;
        count[index]++;
    }

    for (int i = 1; i < 27; i++)
        count[i] += count[i - 1];

    for (int i = n - 1; i >= 0; i--) {
        int index = (pos >= arr[i].size()) ? 0 : arr[i][pos] - 'a' + 1;
        output[count[index] - 1] = arr[i];
        count[index]--;
    }

    for (int i = 0; i < n; i++)
        arr[i] = output[i];
}

void radixSort(vector<string>& arr) {
    size_t maxLen = 0;
    for (auto& s : arr)
        if (s.size() > maxLen) maxLen = s.size();

    for (int pos = maxLen - 1; pos >= 0; pos--)
        countSort(arr, pos);
}

bool isSorted(const vector<string>& arr) {
    for (size_t i = 1; i < arr.size(); ++i)
        if (arr[i - 1] > arr[i])
            return false;
    return true;
}

string randomString(int len, mt19937& rng) {
    uniform_int_distribution<int> dist('a', 'z');
    string s(len, ' ');
    for (int i = 0; i < len; ++i)
        s[i] = char(dist(rng));
    return s;
}

void testStringSorting(int n, int N_max) {
    mt19937 rng(12345);
    vector<string> data;

    for (int i = 0; i < n; i++) {
        uniform_int_distribution<int> lenDist(1, N_max);
        int len = lenDist(rng);
        data.push_back(randomString(len, rng));
    }

    vector<string> data_std = data;

    // Radix Sort
    auto start = chrono::high_resolution_clock::now();
    radixSort(data);
    auto end = chrono::high_resolution_clock::now();
    cout << "Radix sort: " << chrono::duration<double>(end - start).count() << " sec\n";

    if (!isSorted(data)) {
        cout << "Error at Radix sort!\n";
        return;
    }

    // std::sort
    start = chrono::high_resolution_clock::now();
    sort(data_std.begin(), data_std.end());
    end = chrono::high_resolution_clock::now();
    cout << "std::sort: " << chrono::duration<double>(end - start).count() << " sec\n";

    if (!isSorted(data_std)) {
        cout << "Error at std::sort!\n";
        return;
    }
}

int main() {
    testStringSorting(100000, 10);
    return 0;
}
