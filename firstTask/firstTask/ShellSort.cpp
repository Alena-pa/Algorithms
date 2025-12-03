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

vector<long long> generateSmoothSteps(int sizeOfArray) {
    set<long long> numbers = { 1 };
    vector<long long> res;

    while (!numbers.empty()) {
        long long cur = *numbers.begin();
        numbers.erase(numbers.begin());

        if (cur >= sizeOfArray) break;
        res.push_back(cur);

        numbers.insert(cur * 2);
        numbers.insert(cur * 3);
    }
    return res;
}

void ShellSort(vector<long long>& array) {
    int size = array.size();
    vector<long long> steps = generateSmoothSteps(size);
    reverse(steps.begin(), steps.end());

    for (long long step : steps) {
        for (int i = step; i < size; i++) {
            int temp = array[i];
            int j = i;

            while (j >= step && array[j - step] > temp) {
                array[j] = array[j - step];
                j -= step;
            }

            array[j] = temp;
        }
    }
}

void test(vector<long long>& array) {
    vector<long long> arrayForStd = array;

    auto startStd = chrono::steady_clock::now();
    sort(arrayForStd.begin(), arrayForStd.end());
    auto endStd = chrono::steady_clock::now();
    chrono::duration<double> elapsedStd = endStd - startStd;
    cout << "std::sort time: " << elapsedStd.count() << " s\n";

    auto startShell = chrono::steady_clock::now();
    ShellSort(array);
    auto endShell = chrono::steady_clock::now();
    chrono::duration<double> elapsedShell = endShell - startShell;
    cout << "Shell sort time: " << elapsedShell.count() << " s\n";

    if (elapsedStd < elapsedShell) {
        double speedup = elapsedShell.count() / elapsedStd.count();
        cout << "std::sort is " << speedup << "x faster\n";
    }
    else {
        double speedup = elapsedStd.count() / elapsedShell.count();
        cout << "Shell sort is " << speedup << "x faster\n";
    }
}

void testGenerator(const vector<int>& sizes) {
    for (int pow10 : sizes) {
        long long sizeOfArray = pow(10, pow10);
        cout << "\nTEST FOR N = 10^" << pow10 << " (" << sizeOfArray << " elements)\n";

        vector<long long> array = generateRandomArray(sizeOfArray, 1e8);
        test(array);
    }
}

int main() {
    vector<int> test_sizes = { 3, 4, 5, 6 };
    testGenerator(test_sizes);
}