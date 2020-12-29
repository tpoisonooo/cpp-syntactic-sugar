#include <iostream>
#include <tuple>
#include <memory>
#include <cassert>
#include <string>
#include <initializer_list>

#define B_LOOP(i, j)\
    for (size_t i = 0; (i) < (j); ++(i)) {

#define E_LOOP() }
#define EPSILON (1e-6)

template<typename T>
struct Tensor {

    Tensor(std::tuple<size_t, size_t, size_t, size_t> shape) {
        std::tie(n, c, h, w) = shape;
        T* ptr = static_cast<T*>(std::aligned_alloc(64, n * c * h * w * sizeof(T)));
        data = {ptr, [](T* ptr) {
            delete ptr;
        }};
        init();
    }

    Tensor(size_t n, size_t c, size_t h, size_t w):Tensor(std::make_tuple(n, c, h, w)) {
    }

    void init() {
        B_LOOP(i, n)
            const auto base = data.get() + i * n_step();
            B_LOOP(j, c)
                T* ptr = base + j * c_step();
                B_LOOP(k, w*h)
                    ptr[k] = k;
                E_LOOP()
            E_LOOP()
        E_LOOP()
    }

    void print(const std::string& key) {
        std::cout << key << ":" << std::endl;
        T* ptr = data.get();
        B_LOOP(i, n)
            B_LOOP(j, c)
                B_LOOP(k, h)
                    B_LOOP(l, w)
                        auto val = *ptr;
                        ptr++;
                        std::cout << val << ", \t"; 
                    E_LOOP()
                    std::cout << std::endl;
                E_LOOP()
                std::cout << std::endl;
            E_LOOP()
            std::cout << std::endl;
        E_LOOP()
    }

    bool same(const Tensor<T>& t) {
        if (not (n == t.n and c == t.c and h == t.h and w == t.w)) {
            return false;
        }
        const size_t len = n * c * h * w;
        B_LOOP(i, len)
            if (std::abs(static_cast<double>(data.get()[i] - t.data.get()[i])) > EPSILON) {
                return false;
            }
        E_LOOP()
        return true;
    }

    size_t n_step() const {
        return c * h * w;
    }

    size_t c_step() const {
        return h * w;
    }
    
    T* data_ptr(std::initializer_list<size_t> shape) {
        assert(not shape.empty());        

    }

    size_t n, c, h, w;
    std::shared_ptr<T> data;
};

template<typename T>
Tensor<T> nchw_to_nchw4(const Tensor<T> from) {
    assert(from.c % 4 == 0 and 1 == from.n); 
        
    Tensor<T> out(from.n, from.c / 4, from.h, from.w * 4);
    size_t c_loop = from.c / 4;
    const size_t hw = from.h * from.w; 
    for (size_t n = 0; n < from.n; ++n) {
        const size_t base = n * from.c * hw;
        T* ptr_out = out.data.get() + base;
        for (size_t c = 0; c < from.c; c+=4) {
            T* ptr0 = from.data.get() + c * hw + base;
            T* ptr1 = ptr0 + hw;
            T* ptr2 = ptr1 + hw;
            T* ptr3 = ptr2 + hw;

            for (size_t i = 0; i < hw; ++i) {
                ptr_out[0] = *ptr0++;
                ptr_out[1] = *ptr1++;
                ptr_out[2] = *ptr2++;
                ptr_out[3] = *ptr3++;
                ptr_out += 4;
            }
        }
    }
    return out;
}

template<typename T>
Tensor<T> nchw4_to_nchw(const Tensor<T> from) {
    assert(from.w % 4 == 0);
        
    Tensor<T> out(from.n, from.c * 4, from.h, from.w / 4);
    T* ptr_out = out.data.get();
    size_t c_loop = from.c;
    B_LOOP(i, from.n)
        const auto base = i * from.n_step();
        T* ptr = from.data.get() + base;
        T* ptr_out = out.data.get() + base;
        for (size_t c = 0; c < out.c; c += 4) {
            T* ptr0 = ptr_out + c * out.c_step();
            T* ptr1 = ptr0 + out.c_step();
            T* ptr2 = ptr1 + out.c_step();
            T* ptr3 = ptr2 + out.c_step();

            B_LOOP(j, out.c_step())
                *ptr0++ = ptr[0];
                *ptr1++ = ptr[1];
                *ptr2++ = ptr[2];
                *ptr3++ = ptr[3];

                ptr += 4;
            E_LOOP()
        }
    E_LOOP()
    return out;
}

int test_nchw4_convert() {
    Tensor<float> in(1, 4, 8, 8);
    in.print("in");
    auto in_nc4hw4 = nchw_to_nchw4(in);
    in_nc4hw4.print("nc4hw4");
    Tensor<float> in_copy = nchw4_to_nchw(in_nc4hw4);
    in_copy.print("in_copy");
    
    auto same = in.same(in_copy);
    fprintf(stdout, "%d", same);
    Tensor<float> ker(1, 4, 3, 3);
}

template<typename T>
Tensor<T> naive_conv_nchw(Tensor<T> in, Tensor<T> ker) {
    assert(in.c == ker.c); 
    size_t out_h = in.h - ker.h + 1;
    size_t out_w = in.w - ker.w + 1;
    Tensor<T> out(in.n, ker.n, out_h, out_w);

    
}

int test_convolution() {
    
}

int main() {
    return 0;
}
