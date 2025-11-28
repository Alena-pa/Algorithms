#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <chrono>

using namespace std;

void countSort(vector<long long>& a, int n, long long digit) {
    int size = a.size();
    vector<long long> out(size);

    if (n < 2) return;

    vector<int> cnt(n, 0);

    for (long long x : a) {
        int d = (x / digit) % n;
        cnt[d]++;
    }

    for (int i = 1; i < n; i++)
        cnt[i] += cnt[i - 1];

    for (int i = size - 1; i >= 0; i--) {
        int d = (a[i] / digit) % n;
        out[--cnt[d]] = a[i];
    }

    a = out;
}

void radixSort(vector<long long>& a, int n) {
    long long base1 = 1;
    long long base2 = 1LL * n;
    long long base3 = 1LL * n * n;

    countSort(a, n, base1);
    countSort(a, n, base2);
    countSort(a, n, base3);
}

vector<long long> makeRandom(int n) {
    random_device rd;
    mt19937_64 gen(rd());
    long long maxv = 1LL * n * n * n - 1;

    uniform_int_distribution<long long> dist(0, maxv);

    vector<long long> a(n);
    for (long long& x : a)
        x = dist(gen);

    return a;
}

void testSorting(int n) {
    vector<long long> a = makeRandom(n);
    vector<long long> b = a;

    auto t1 = chrono::high_resolution_clock::now();
    radixSort(a, n);
    auto t2 = chrono::high_resolution_clock::now();

    double t_radix = chrono::duration<double>(t2 - t1).count();

    auto t3 = chrono::high_resolution_clock::now();
    sort(b.begin(), b.end());
    auto t4 = chrono::high_resolution_clock::now();

    double t_std = chrono::duration<double>(t4 - t3).count();

    if (a == b)
        cout << "OK\n";
    else
        cout << "ERROR: sorting incorrect!\n";

    cout << "\nResults of sorting\n";
    cout << "Radix sort: " << t_radix << " sec\n";
    cout << "std::sort:  " << t_std << " sec\n";
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n = 50000;
    testSorting(n);
}