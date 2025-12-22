#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

void searchCrossPairs(const vector<int>& leftHalf, const vector<int>& rightHalf, int targetSum, bool& pairFound) {
    size_t leftPointer = 0;
    size_t rightPointer = rightHalf.size();

    if (rightPointer == 0) return;
    --rightPointer;

    while (leftPointer < leftHalf.size() && rightPointer < rightHalf.size()) {
        long long currentSum = (long long)leftHalf[leftPointer] + rightHalf[rightPointer];
        if (currentSum == targetSum) {
            cout << "(" << leftHalf[leftPointer] << ", " << rightHalf[rightPointer] << ")\n";
            pairFound = true;
            ++leftPointer;
            if (rightPointer == 0) break;
            --rightPointer;
        }
        else if (currentSum < targetSum) {
            ++leftPointer;
        }
        else {
            if (rightPointer == 0) break;
            --rightPointer;
        }
    }
}

void divideAndConquerSearch(vector<int>& array, int targetSum, int segmentStart, int segmentEnd, bool& pairFound) {
    if (segmentStart >= segmentEnd) {
        return;
    }

    int midpoint = segmentStart + (segmentEnd - segmentStart) / 2;

    divideAndConquerSearch(array, targetSum, segmentStart, midpoint, pairFound);
    divideAndConquerSearch(array, targetSum, midpoint + 1, segmentEnd, pairFound);

    vector<int> leftSegment(array.begin() + segmentStart, array.begin() + midpoint + 1);
    vector<int> rightSegment(array.begin() + midpoint + 1, array.begin() + segmentEnd + 1);

    sort(leftSegment.begin(), leftSegment.end());
    sort(rightSegment.begin(), rightSegment.end());

    searchCrossPairs(leftSegment, rightSegment, targetSum, pairFound);
}

void findPairsWithGivenSum(const vector<int>& inputArray, int targetSum) {
    if (inputArray.size() < 2) {
        cout << "No pairs found.\n";
        return;
    }

    vector<int> workingArray = inputArray;
    bool foundAnyPair = false;
    divideAndConquerSearch(workingArray, targetSum, 0, workingArray.size() - 1, foundAnyPair);

    if (!foundAnyPair) {
        cout << "No pairs found.\n";
    }
}

int main() {
    vector<int> numbers = { 3, 1, 5, 2, 4 };
    int desiredSum = 6;
    findPairsWithGivenSum(numbers, desiredSum);
    return 0;
}