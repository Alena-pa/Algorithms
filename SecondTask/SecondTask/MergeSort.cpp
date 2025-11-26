#include <iostream>
#include <string>

struct Node {
    std::string name;
    std::string phone;
    Node* next;

    Node(const std::string& n, const std::string& p)
        : name(n), phone(p), next(nullptr) {
    }
};

struct List {
    Node* head;
    List() : head(nullptr) {}
};

List* makeList() {
    return new List();
}

void freeList(List* lst) {
    Node* cur = lst->head;
    while (cur) {
        Node* tmp = cur;
        cur = cur->next;
        delete tmp;
    }
    delete lst;
}

int size(List* lst) {
    int cnt = 0;
    Node* cur = lst->head;
    while (cur) {
        cnt++;
        cur = cur->next;
    }
    return cnt;
}

std::string headName(List* lst) {
    return lst->head->name;
}

std::string headPhone(List* lst) {
    return lst->head->phone;
}

void moveNodes(List* src, List* dst, int k) {
    while (k-- > 0 && src->head) {
        Node* n = src->head;
        src->head = src->head->next;
        n->next = dst->head;
        dst->head = n;
    }
}

List* mergeLists(List* a, List* b, bool byName) {
    List* res = makeList();
    List* tmp = makeList();

    while (size(a) != 0 && size(b) != 0) {
        std::string va = byName ? headName(a) : headPhone(a);
        std::string vb = byName ? headName(b) : headPhone(b);

        if (va < vb) moveNodes(a, tmp, 1);
        else moveNodes(b, tmp, 1);
    }

    if (size(b) == 0) moveNodes(a, tmp, size(a));
    else moveNodes(b, tmp, size(b));

    while (tmp->head) moveNodes(tmp, res, 1);

    freeList(a);
    freeList(b);
    freeList(tmp);

    return res;
}

List* mergeSort(List* lst, bool byName) {
    int n = size(lst);
    if (n <= 1) return lst;

    List* left = makeList();
    List* right = makeList();

    moveNodes(lst, left, n / 2);
    moveNodes(lst, right, n - n / 2);

    freeList(lst);

    left = mergeSort(left, byName);
    right = mergeSort(right, byName);

    return mergeLists(left, right, byName);
}

void push(List* lst, const std::string& name, const std::string& phone) {
    Node* n = new Node(name, phone);
    n->next = lst->head;
    lst->head = n;
}

void print(List* lst) {
    Node* cur = lst->head;
    while (cur) {
        std::cout << cur->name << " - " << cur->phone << "\n";
        cur = cur->next;
    }
}

int main() {
    List* lst = makeList();
    push(lst, "Charlie", "555");
    push(lst, "Alice", "222");
    push(lst, "Bob", "444");

    std::cout << "Before:\n";
    print(lst);

    lst = mergeSort(lst, true);

    std::cout << "\nAfter:\n";
    print(lst);

    freeList(lst);
    return 0;
}
