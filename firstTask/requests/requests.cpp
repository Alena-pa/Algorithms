#include <iostream>
#include <vector>
#include <random>
using namespace std;

void print_vec(const vector<int>& v) {
    for (int x : v) cout << x << " ";
    cout << "\n";
}

void generate_random(vector<int>& v, int n, int max_val) {
    mt19937 rnd(time(nullptr));
    for (int i = 0; i < n; i++)
        v.push_back(rnd() % max_val);
}

int vmax(const vector<int>& v) {
    int mx = 0;
    for (int x : v) mx = max(mx, x);
    return mx;
}

vector<int> count_sort(const vector<int>& v) {
    int K = vmax(v) + 1;
    vector<int> cnt(K, 0);
    for (int x : v) cnt[x]++;
    return cnt;
}

void build_prefix(vector<int>& cnt) {
    for (int i = 1; i < (int)cnt.size(); i++)
        cnt[i] += cnt[i - 1];
}

int query(const vector<int>& pref, int l, int r) {
    if (l == 0) return pref[r];
    return pref[r] - pref[l - 1];
}

int main() {
    int n, max_el;
    cout << "Enter array size and max element: ";
    cin >> n >> max_el;

    vector<int> v;
    generate_random(v, n, max_el);

    cout << "Generated array: ";
    print_vec(v);

    vector<int> freq = count_sort(v);
    cout << "Frequency array: ";
    print_vec(freq);

    build_prefix(freq);
    cout << "Prefix sums: ";
    print_vec(freq);

    int q;
    cout << "Enter number of queries: ";
    cin >> q;

    while (q--) {
        int l, r;
        cout << "Enter l and r: ";
        cin >> l >> r;
        cout << "Count in range [" << l << "," << r << "] = " << query(freq, l, r) << "\n";
    }

    return 0;
}
