#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <limits>

using namespace std;

void insertionSort(vector<int>& arr, int left, int right) {
    for (int i = left + 1; i <= right; ++i) {
        int key = arr[i];
        int j = i - 1;
        while (j >= left && arr[j] > key) {
            arr[j + 1] = arr[j];
            --j;
        }
        arr[j + 1] = key;
    }
}

void merge(vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<int> L(n1), R(n2);
    for (int i = 0; i < n1; ++i) L[i] = arr[left + i];
    for (int j = 0; j < n2; ++j) R[j] = arr[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        }
        else {
            arr[k++] = R[j++];
        }
    }
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];
}

void hybridMergeSort(vector<int>& arr, int left, int right, int m) {
    if (left >= right) return;
    if (right - left + 1 <= m) {
        insertionSort(arr, left, right);
        return;
    }
    int mid = left + (right - left) / 2;
    hybridMergeSort(arr, left, mid, m);
    hybridMergeSort(arr, mid + 1, right, m);
    merge(arr, left, mid, right);
}

void hybridMergeSort(vector<int>& arr, int m) {
    if (!arr.empty()) {
        hybridMergeSort(arr, 0, arr.size() - 1, m);
    }
}

void test(vector<int> array, int m) {
    vector<int> expected = array;
    sort(expected.begin(), expected.end());

    vector<int> actual = array;
    hybridMergeSort(actual, m);

    if (actual == expected) {
        cout << "OK\n";
    }
    else {
        cout << "ERROR\n";
    }
}

vector<int> generateRandomArray(int n) {
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> dist(numeric_limits<int>::min(), numeric_limits<int>::max());
    vector<int> arr(n);
    for (int& x : arr) x = dist(gen);
    return arr;
}

int main() {
    vector<int> arr = generateRandomArray(10000);
    test(arr, 32);
    return 0;
}