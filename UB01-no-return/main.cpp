#include <iostream>

int func2() {}

int func1() {
    return func2();
}

int main() {
    return func1();
}
