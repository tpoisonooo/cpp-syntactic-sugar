#include <cmath>
#include <random>
#include <cassert>

template <typename T>
struct Rect {
    T left = 0.f, top = 0.f, right = 0.f, bottom = 0.f;
    Rect() = default;
    Rect(T l, T t, T r, T b)
        : left(l), top(t), right(r), bottom(b) {}

    inline T width() const { return right - left; }

    inline T height() const { return bottom - top; }
};

void crop_resize_bgr(size_t w, size_t h) {
    if (w != h) {
        fprintf(stdout, "crash !  %ld %ld\n", w, h);
        assert(w == h);
    }
    return;
}

int example1() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(1.0, 1000.0);

    while(true) {
        float x_center = dis(gen);
        float y_center = dis(gen);
        float max_length = dis(gen);
        Rect<float> crop_rect(x_center - max_length, y_center - max_length, x_center + max_length, y_center + max_length);
        
        //fprintf(stdout, "%f %f %f %f\n", crop_rect.left, crop_rect.top, crop_rect.right, crop_rect.bottom);
        fprintf(stdout, "diff %f \n", crop_rect.width() - crop_rect.height());
        crop_resize_bgr(crop_rect.width(), crop_rect.height());
    }
    return 0;
}



int main() {
    example1();
}
