#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <chrono>

using namespace std;

void countingSortByDigit(vector<long long>& array, int base, long long divisor) {
    int size = array.size();
    if (size <= 1) return;

    vector<long long> output(size);
    vector<int> count(base, 0);

    for (long long value : array) {
        int digit = (value / divisor) % base;
        count[digit]++;
    }

    for (int i = 1; i < base; ++i) {
        count[i] += count[i - 1];
    }

    for (int i = size - 1; i >= 0; --i) {
        int digit = (array[i] / divisor) % base;
        output[--count[digit]] = array[i];
    }

    array = output;
}

void radixSort(vector<long long>& array, int n) {
    long long firstDigitWeight = 1;
    long long secondDigitWeight = 1LL * n;
    long long thirdDigitWeight = 1LL * n * n;

    countingSortByDigit(array, n, firstDigitWeight);
    countingSortByDigit(array, n, secondDigitWeight);
    countingSortByDigit(array, n, thirdDigitWeight);
}

vector<long long> generateRandomArray(int n) {
    random_device device;
    mt19937_64 generator(device());
    long long maxValue = 1LL * n * n * n - 1;
    uniform_int_distribution<long long> distribution(0, maxValue);

    vector<long long> array(n);
    for (long long& value : array) {
        value = distribution(generator);
    }
    return array;
}

void runSortingTest(int n) {
    vector<long long> array = generateRandomArray(n);
    vector<long long> reference = array;

    radixSort(array, n);
    sort(reference.begin(), reference.end());

    if (array == reference) {
        cout << "OK\n";
    }
    else {
        cout << "ERROR: sorting incorrect!\n";
    }
}

int main() {
    int n = 50000;
    runSortingTest(n);
    return 0;
}