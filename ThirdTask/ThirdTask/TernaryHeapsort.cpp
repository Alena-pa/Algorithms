#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>

using namespace std;

void siftDown(std::vector<int>& arr, int n, int index) {
    while (true) {
        int firstChild = 3 * index + 1;
        int secondChild = 3 * index + 2;
        int thirdChild = 3 * index + 3;

        int largest = index;

        if (firstChild < n && arr[firstChild] > arr[largest]) largest = firstChild;
        if (secondChild < n && arr[secondChild] > arr[largest]) largest = secondChild;
        if (thirdChild < n && arr[thirdChild] > arr[largest]) largest = thirdChild;

        if (largest == index) break;

        std::swap(arr[index], arr[largest]);
        index = largest;
    }
}

void buildTernaryHeap(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = (n - 2) / 3; i >= 0; i--) {
        siftDown(arr, n, i); 
    }
}

void ternaryHeapSort(std::vector<int>& arr) {
    int n = arr.size();

    buildTernaryHeap(arr);

    for (int i = n - 1; i > 0; i--) {
        std::swap(arr[0], arr[i]);
        siftDown(arr, i, 0);
    }
}

bool isSorted(const vector<int>& value) {
    for (size_t i = 1; i < value.size(); i++) {
        if (value[i - 1] > value[i]) return false;
    }

    return true;
}

bool testSortSpeed(const string& name, vector<int> data, void (*sortFunc)(vector<int>&)) {
    auto start = chrono::high_resolution_clock::now();

    sortFunc(data);

    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> duration = end - start;

    cout << name << " takes " << duration.count() << " seconds\n";

    if (!isSorted(data)) {
        cout << "Error! Array adter" << name << " is not sorted!\n";
        return false;
    }

    return true;
}

vector<int> generateRandom(int n) {
    mt19937 rng(12345);
    vector<int> v(n);
    for (int& x : v) x = rng();
    return v;
}

int main()
{
    vector<int> data = generateRandom(100000);

    if (!testSortSpeed("std::sort", data, [](vector<int>& v) { sort(v.begin(), v.end()); })) {
        return 1;
    }

    if (!testSortSpeed("ternary heap sort", data, ternaryHeapSort)) {
        return 1;
    }

    return 0;
}
