#include <iostream>
#include <vector>

long long mergeAndCount(std::vector<int>& arr, std::vector<int>& temp, int left, int middle, int right) {
    int leftPos = left;
    int rightPos = middle + 1;
    int mergePos = left;
    long long inversionCount = 0;

    while (leftPos <= middle && rightPos <= right) {
        if (arr[leftPos] <= arr[rightPos]) {
            temp[mergePos++] = arr[leftPos++];
        }
        else {
            inversionCount += (middle - leftPos + 1);
            temp[mergePos++] = arr[rightPos++];
        }
    }

    while (leftPos <= middle) temp[mergePos++] = arr[leftPos++];
    while (rightPos <= right) temp[mergePos++] = arr[rightPos++];

    for (int i = left; i <= right; i++) arr[i] = temp[i];

    return inversionCount;
}

long long sortAndCount(std::vector<int>& arr, std::vector<int>& temp, int left, int right) {
    if (left >= right) return 0;

    int middle = (left + right) / 2;
    long long count = 0;

    count += sortAndCount(arr, temp, left, middle);
    count += sortAndCount(arr, temp, middle + 1, right);
    count += mergeAndCount(arr, temp, left, middle, right);

    return count;
}

long long countInterestingPairs(const std::vector<int>& array) {
    std::vector<int> arrCopy = array;
    std::vector<int> temp(arrCopy.size());
    return sortAndCount(arrCopy, temp, 0, arrCopy.size() - 1);
}

int main() {
    std::vector<int> exampleArray = { 5, 3, 2, 4, 1 };
    std::cout << "Number of interesting pairs: " << countInterestingPairs(exampleArray) << std::endl;
    return 0;
}
