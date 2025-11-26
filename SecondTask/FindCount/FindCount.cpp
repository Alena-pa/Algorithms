#include <iostream>
#include <vector>

void merge(std::vector<int>& arr, std::vector<int>& temp, int left, int middle, int right) {
    int i = left;
    int j = middle + 1;
    int k = left;

    while (i <= middle && j <= right) {
        if (arr[i] <= arr[j]) temp[k++] = arr[i++];
        else temp[k++] = arr[j++];
    }

    while (i <= middle) temp[k++] = arr[i++];
    while (j <= right) temp[k++] = arr[j++];

    for (int p = left; p <= right; p++) arr[p] = temp[p];
}

void mergeSort(std::vector<int>& arr, std::vector<int>& temp, int left, int right) {
    if (left >= right) return;

    int middle = (left + right) / 2;
    mergeSort(arr, temp, left, middle);
    mergeSort(arr, temp, middle + 1, right);
    merge(arr, temp, left, middle, right);
}

void findPairsWithSum(const std::vector<int>& array, int target) {
    std::vector<int> sorted = array;
    std::vector<int> temp(sorted.size());
    mergeSort(sorted, temp, 0, sorted.size() - 1);

    int left = 0;
    int right = sorted.size() - 1;
    bool found = false;

    while (left < right) {
        int sum = sorted[left] + sorted[right];
        if (sum == target) {
            std::cout << "(" << sorted[left] << ", " << sorted[right] << ")\n";
            found = true;
            left++;
            right--;
        }
        else if (sum < target) {
            left++;
        }
        else {
            right--;
        }
    }

    if (!found) std::cout << "No pairs found.\n";
}

int main() {
    std::vector<int> array = { 3, 1, 5, 2, 4 };
    int S = 6;

    findPairsWithSum(array, S);
    return 0;
}
