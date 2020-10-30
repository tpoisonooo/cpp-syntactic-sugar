// range(start, end, step)
// range(start, end)
// range(1, 10)
// range(1, 10, 2)
// range(1, 12, 1.5)
#include <iostream>

namespace detail_range {

template <typename T>
class iterator {
private:
    size_t m_cursor;
    T m_value, m_step;
public:
    iterator(size_t cur_start, T begin, T step): m_cursor(cur_start), m_value(begin), m_step(step) {
        m_value += (m_step * m_cursor);
    }

    T operator*() const {
        return m_value;
    }

    bool operator!=(const iterator& rhs) const {
        return (m_cursor != rhs.m_cursor);
    }

    iterator& operator++(void) {
        m_value += m_step;
        ++ m_cursor;
        return (*this);
    }
};

template <typename T>
class impl {
private:
    T m_begin, m_end, m_step;
    size_t m_count;

    size_t get_count() const {
        if (m_step > 0 and m_begin >= m_end) {
            throw std::logic_error("begin >= end");
        }
        if (m_step < 0 and m_begin <= m_end) {
            throw std::logic_error("begin <= end");
        }
        auto x = static_cast<size_t>((m_end - m_begin) / m_step);
        if (x * m_step + m_begin != m_end) {
                ++x;
        } 
        return x;
    }

public:
    impl(T begin, T end, T step): m_begin(begin), m_end(end), m_step(step), m_count(get_count()) {}
    using const_itra = const iterator<T>;    

    const_itra begin(void) const {
        return {0, m_begin, m_step};
    }

    const_itra end(void) const {
        return {m_count, m_begin, m_step}; 
    }
};

}

template <typename T>
detail_range::impl<T> range(T x, T y) {
    return {x, y, 1};
}

template <typename T, typename U>
auto range(T x, T y, U z) -> detail_range::impl<decltype(x + z)> {
    return detail_range::impl<decltype(x+z)> {x, y, z};
}

int main() {
    for (auto i: range(1, 10)) {
        std::cout << i << ",";
    }
    std::cout << std::endl;

    for (auto i: range(1, 5, 1)) {
        std::cout << i << ",";
    }
    std::cout << std::endl;

    for (auto i: range(1, 5, 1.5)) {
        std::cout << i << ",";
    }
    std::cout << std::endl;

    for (auto i: range(14, 5, -1)) {
        std::cout << i << ",";
    }
    std::cout << std::endl;
}
