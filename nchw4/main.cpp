#include <iostream>
#include <tuple>
#include <memory>
#include <cassert>
#include <string>
#include <vector>
#include <chrono>

using Clock = std::chrono::high_resolution_clock;

class Timer {
public:
    explicit Timer(const std::string& name)
        : name_(name) {
        start_ = Clock::now();
    }

    ~Timer() {
        stop_ = Clock::now();
        auto interval = std::chrono::duration_cast<std::chrono::microseconds>(
                            stop_ - start_)
                            .count();
        fprintf(stdout, "%s cost %ld\n", name_.c_str(), interval);
    }

private:
    std::string name_;
    Clock::time_point start_;
    Clock::time_point stop_;
};

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
                    ptr[k] = j%2;
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
    
    T* ptr_at(const std::vector<size_t>& shape) const {
        assert(shape.size() == 4);
        T* ptr = data.get();
        ptr += shape[0] * n_step();
        ptr += shape[1] * c_step();
        ptr += shape[2] * w;
        ptr += shape[3];
        return ptr;
    }

    size_t n, c, h, w;
    std::shared_ptr<T> data;
};

template<typename T>
Tensor<T> nchw_to_nchw4(const Tensor<T>& from) {
    assert(from.c % 4 == 0); 
        
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
Tensor<T> nchw4_to_nchw(const Tensor<T>& from) {
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

template<typename T, size_t X>
Tensor<T> im2colX(const Tensor<T>& in, const Tensor<T>& ker) {
   Tensor<T> out(1, 1, 1, 1); 
   return out;
}

template<typename T>
Tensor<T> naive_conv_nchw(const Tensor<T>& in, const Tensor<T>& ker) {
    assert(in.c == ker.c); 
    size_t out_h = in.h - ker.h + 1;
    size_t out_w = in.w - ker.w + 1;
    Tensor<T> out(in.n, ker.n, out_h, out_w);

    B_LOOP(on, out.n)
        B_LOOP(oc, out.c)
            B_LOOP(oh, out.h)
                B_LOOP(ow, out.w)
                    T sum = 0;
                    for(size_t start_h = oh; start_h < oh + ker.h; ++start_h) {
                        for(size_t start_w = ow; start_w < ow + ker.w; ++start_w) {
                            for(size_t ic = 0; ic < in.c; ++ic) {
                                sum += (*in.ptr_at({on, ic, start_h, start_w})) * (*ker.ptr_at({oc, ic, start_h - oh, start_w - ow})); 
                            }
                        }
                    }
                    *(out.ptr_at({on, oc, oh, ow})) = sum;
                E_LOOP()
            E_LOOP()
        E_LOOP()
    E_LOOP()
    return out;
}

template<typename T>
Tensor<T> naive_conv_nchw4(const Tensor<T>& in, const Tensor<T>& ker) {
    assert(in.c == ker.c); 
    size_t out_h = in.h - ker.h + 1;
    size_t out_w = in.w/4 - ker.w/4 + 1;
    Tensor<T> out(in.n, ker.n, out_h, out_w);

    B_LOOP(on, out.n)
        B_LOOP(oc, out.c)
            B_LOOP(oh, out.h)
                B_LOOP(ow, out.w)
                    T sum = 0;
                    for(size_t ic = 0; ic < in.c; ++ic) {
                        for(size_t start_h = oh; start_h < oh + ker.h; ++start_h) {
                            for(size_t start_w = ow; start_w < ow + ker.w / 4; start_w += 1) {
                                const auto in_ptr = in.ptr_at({on, ic, start_h, start_w * 4});
                                const auto ker_ptr = ker.ptr_at({oc, ic, start_h - oh, (start_w - ow) * 4});
                                sum += in_ptr[0] * ker_ptr[0];
                                sum += in_ptr[1] * ker_ptr[1];
                                sum += in_ptr[2] * ker_ptr[2];
                                sum += in_ptr[3] * ker_ptr[3];
                            }
                        }
                    }
                    *(out.ptr_at({on, oc, oh, ow})) = sum;
                E_LOOP()
            E_LOOP()
        E_LOOP()
    E_LOOP()
    return out;
}

int test_convolution() {
    Tensor<float> in(1, 4, 8, 8);
    Tensor<float> ker(1, 4, 3, 3);
    auto out_nchw = naive_conv_nchw(in, ker);
    out_nchw.print("naive_conv");
}

int test_convolution_nchw4() {
    Tensor<float> in(1, 32, 8, 8);
    auto in_convert = nchw_to_nchw4(in);
    in_convert.print("in_convert");

    Tensor<float> ker(32, 32, 3, 3);
    auto ker_convert = nchw_to_nchw4(ker);
    ker_convert.print("ker_convert");

    auto out_nchw = naive_conv_nchw(in, ker);

    auto out = naive_conv_nchw4(in_convert, ker_convert);
    out.print("naive_conv_nchw4");

    assert(out_nchw.same(out));
}

void test_fp32_conv_speedup(size_t in, size_t ic, size_t ih, size_t iw, size_t on, size_t kh, size_t kw, size_t loop) {
    Tensor<float> _in(in, ic, ih, iw);
    Tensor<float> _ker(on, ic, kh, kw);
    {
        Timer t1("normal");

        B_LOOP(i, loop)
            naive_conv_nchw(_in, _ker);
        E_LOOP()

    }
    {
        auto _in_convert = nchw_to_nchw4(_in);
        auto _ker_convert = nchw_to_nchw4(_ker);
        Timer t2("nchw4");

        B_LOOP(i, loop)
            naive_conv_nchw4(_in_convert, _ker_convert);
        E_LOOP()
    }
}

int main() {
    test_nchw4_convert();
    test_convolution();
    test_convolution_nchw4();
    test_fp32_conv_speedup(1, 8, 224, 224, 8, 3, 3, 1);
    test_fp32_conv_speedup(1, 8, 112, 112, 8, 5, 5, 1);
    test_fp32_conv_speedup(1, 64, 64, 64, 64, 3, 3, 1);
    test_fp32_conv_speedup(1, 64, 32, 32, 64, 1, 1, 1);
    return 0;
}
