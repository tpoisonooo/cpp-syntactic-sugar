#include <type_traits>
#include <string>
#include <iostream>

template<typename T>
class Optional {
public:
    using data_t = typename std::aligned_storage<sizeof(T), std::alignment_of<T>::value>::type;

    Optional() {}

    Optional(const T& v) {
        create(v);
    }

    Optional(const Optional& opt) {
        copy(opt);
    }

    ~Optional() {
        destory();
    }

    template<class... Args>
    void emplace(Args && ... args) {
        create(std::forward<Args>(args)...);    
    }

    void copy(const Optional& opt) {
        destory();
        new (&m_data) T(*(T*)(&(opt.m_data)));
        m_init = true;
    }

    void destory() {
        if (m_init) {
            ((T*)(&m_data))->~T();
        }
    }

    template<class... Args>
    void create(Args&&... args) {
        new (&m_data) T(std::forward<Args>(args)...);
        m_init = true;
    }

private:
    data_t m_data;
    bool m_init;
};

struct Node {
    Node(int _a, int _b): a(_a), b(_b) {}
    int a; 
    int b;
};

int main() {
    Optional<int> iopt;
    Optional<std::string> sopt("abc");

    Optional<Node> nopt;
    nopt.emplace(1, 2);

}
