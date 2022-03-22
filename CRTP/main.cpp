#include <iostream>
#include <vector>

// class Vec {
//     std::vector<double> elems;
//     public:
//     Vec(size_t n) : elems(n) {}
//     double &operator[](size_t i) {return elems[i];}
//     double operator[](size_t i) const {return elems[i];}
//     size_t size() const {return elems.size();}
// };
// 
// Vec operator(Vec const& u, Vec const& v) {
//     Vec sum(u.size());
//     for (size_t i = 0; i < u.size(); ++i) {
//         sum[i] = u[i] + v[i];
//     }
//     return sum;
// }


template <typename E>
class VecExpr {
    public:
    double operator[](size_t i) const {
        return static_cast<E const&>(*this)[i];
    }

    size_t size() const {
        return static_cast<E const&>(*this).size();
    }
};


class Vec: public VecExpr<Vec> {
    std::vector<double> elems;
    public:
    double operator[](size_t i) const {return elems[i];}
    double &operator[](size_t i) {return elems[i];}
    size_t size() const {return elems.size();}


    Vec(size_t n): elems(n) {}
    Vec(std::initializer_list<double> init): elems(init) {} 

    template<typename E>
    Vec(VecExpr<E> const& expr): elems(expr.size()) {
        for (size_t i = 0; i < expr.size(); ++i) {
            elems[i] = expr[i];
        }
    }
};

template<typename E1, typename E2>
class VecSum: public VecExpr<VecSum<E1, E1>> {
    E1 const& _u;
    E2 const& _v;

    public:
    VecSum(E1 const&u, E2 const& v): _u(u), _v(v) {}

    double operator[](size_t i) const { return _u[i] + _v[i];}
    size_t size() const {return _v.size();}
};


template<typename E1, typename E2>
VecSum<E1, E2> operator+(VecExpr<E1> const&u, VecExpr<E2> const&v) {
    return VecSum<E1, E2>(*static_cast<const E1*>(&u), *static_cast<const E2*>(&v));
}

int main() {
    Vec v0 = {1., 2., 3.};
    Vec v1 = {1., 2., 3.};
    Vec v2 = {1., 2., 3.};

    auto sum = v0 + v1 + v2;

    // 1) first call operator+
    // E1=VecExpr<Vec>, E2=VecExpr<Vec>
    // construct VecSum<Vec, Vec>
    // 
    // 2) second call operator+
    // E1=VecSum<Vec, Vec>, E2=VecExpr<Vec>
    // construct VecSum<VecSum<Vec, Vec>, Vec>
    // 
    // this is typeid(sum), **only expr, not execute**

    for(int i = 0; i < sum.size(); ++i) {
        fprintf(stdout, "%f ", sum[i]);
        // 3) when fetching index with operator[]
        // execute VecSum::operator[]
        // return VecSum<Vec,Vec>[i] + Vec[i]
        // return Vec[i] + Vec[i] + Vec[i]

        // real execution happens in line 90
    } 
}
