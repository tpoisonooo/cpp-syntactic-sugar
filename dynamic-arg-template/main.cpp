#include <iostream>
#include <type_traits>

template <typename FUNC, typename... ARGS>
auto func_wrapper(FUNC&& f, ARGS && ... args) -> decltype(f(std::forward<ARGS>(args)...)) {
    return f(std::forward<ARGS>(args)...);
}

void test1(int a) {
    fprintf(stdout, "%d\n", a);
}

void test2(std::string a, const std::string& b) {
    fprintf(stdout, "%s\n", (a+b).c_str());
}

int test_func_wrapper() {
    func_wrapper(test1, 1);
    func_wrapper(test2, "abc", "def");
    return 0;
}

// use default implementation
template <typename T>
void print(T a) {
    std::cout << a << std::endl; 
}

template <typename T, typename... Args>
void print(T begin, Args... other) {
    std::cout << begin << std::endl;
    print(other...);
}

template <typename... Args> class Sum;
template <typename T, typename... Args>
class Sum<T, Args...> 
{
public:
    enum { size = Sum<T>::size + Sum<Args...>::size };
};

template <typename T>
class Sum<T>
{
public:
    enum { size = sizeof(T) };
};

template <typename... Args> class Tum;
template <typename T, typename... Args>
struct Tum<T, Args...>: std::integral_constant<int, Tum<T>::value + Tum<Args...>::value> {};
template <typename T>
struct Tum<T>: std::integral_constant<int, sizeof(T)> {};

template <unsigned n>
struct Fib: std::integral_constant<int, n + Fib<n-1>::value> {};

template <>
struct Fib<0>: std::integral_constant<int, 1> {};


// use comma expression 
template <typename... Args>
void multi_para(Args && ... args) {
   int x[] = {(print(std::forward<Args>(args)...), 0)};
}

void test_dynamic_param() {
    print(0, 1, 2, 3, 4);
    print(Sum<float, int, float>::size);
    multi_para(0, 1, 2, 3, 4);
    print(Fib<5>::value, Fib<22>::value);

    print(Tum<float, int, float>::value);
}

int main() {
    test_func_wrapper();
    test_dynamic_param();
    return 0;
}
