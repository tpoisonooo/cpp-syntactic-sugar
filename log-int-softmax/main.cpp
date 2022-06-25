#include "npy.h"
#include <cassert>
#include <cmath>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

static inline int32_t int_polynominal(const int32_t x, const float s)
{
    // ax**2 + bx + c
    const float coef0 = 0.35815147;
    const float coef1 = 0.96963238 / coef0;
    const float coef2 = 1.0 / coef0;

    const int32_t b_int = floor(coef1 * s);
    const int32_t c_int = floor(coef2 * s * s);
    return x * (x + b_int) + c_int;
}

static inline int64_t int_exp(int32_t x, float s)
{
#define LN2 (-0.6931f)
    const int n = 30;
    const int x0_int = floor(LN2 / s);

    x = std::max(x, n * x0_int);
    const int q = floor(x * 1.0f / x0_int);
    const int r = x - x0_int * q;
    int64_t exp_int = int_polynominal(r, 1.0f / s);

    exp_int = std::max((int64_t)0, (int64_t)floor(exp_int * pow(2, (n - q))));
    // fprintf(stdout, "[x,r,exp_int   %d\t,%d\t,%ld\t]\n", x, r, exp_int);
    return exp_int;
#undef LN2
}

static inline float fast_pow2_multiply_3(const int32_t index)
{
    //   assert(index <= 30 && index >= -1);
    static float table[] = {
        1.5f, 3, 6, 12, 24, 48,
        96, 192, 384, 768, 1536, 3072,
        6144, 12288, 24576, 49152, 98304, 196608,
        393216, 786432, 1572864, 3145728, 6291456, 12582912,
        25165824, 50331648, 100663296, 201326592, 402653184, 805306368,
        1610612736, 3221225472
    };
    return table[index + 1];
}

static inline int32_t find_first_one(int32_t v)
{
    int pos = 0;

    if (v > 0xffff)
    {
        v >>= 16;
        pos += 16;
    }

    if (v > 0xff)
    {
        v >>= 8;
        pos += 8;
    }

    if (v > 0xf)
    {
        v >>= 4;
        pos += 4;
    }

    if (v > 0x3)
    {
        v >>= 2;
        pos += 2;
    }

    if (v > 0x1)
    {
        v >>= 1;
        pos += 1;
    }

    return pos;
}

static inline int32_t float2int8(float v)
{
    int int32 = static_cast<int>(round(v));
    if (int32 > 127) return 127;
    if (int32 < -127) return -127;
    return int32;
}

static void write_file(int32_t* ptr, int32_t* out, float scale, int len) {
    static int index = 0;
    char filename[64] = {0};
    sprintf(filename, "lis_%d", index++);

    std::ofstream fout;
    fout.open(std::string(filename), std::ios::out);
    fout << scale << std::endl;

    for (int i = 0; i < len; ++i) {
        fout << ptr[i] << ",";
    }
    fout << std::endl;

    for (int i = 0; i < len; ++i) {
        fout << out[i] << ",";
    }
    fout << std::endl;
    fout.flush();
    fout.close();
}

int log_int_softmax(int32_t* ptr, int64_t* buffer, int8_t* out, const int len, float scale)
{
    // std::vector<int32_t> from;
    // std::vector<int32_t> to;

    int32_t max = ptr[0];
    for (int i = 0; i < len; ++i)
    {
        // from.push_back(static_cast<int32_t>(ptr[i]));
        if (max < ptr[i])
        {
            max = ptr[i];
        }
    }

    int64_t sum = 0;
    for (int i = 0; i < len; ++i)
    {
        ptr[i] = ptr[i] - max;
        buffer[i] = int_exp(ptr[i], scale);
        sum += buffer[i];
    }

    const int UINT4_MAX = 15;
    for (int i = 0; i < len; ++i)
    {
        const int32_t val = int32_t(sum * 1.f / buffer[i] + 0.5f);
        int32_t power = find_first_one(val);
        float big = fast_pow2_multiply_3(power - 1);

        if (val >= big) {
            power += 1;
        }

        if (power > UINT4_MAX) {
            out[i] = -1;
            // to.push_back(static_cast<int32_t>(-1));
            continue;
        }

        // to.push_back(static_cast<int32_t>(power));
        out[i] = power;
    }

    // write_file(from.data(), to.data(), scale, from.size());
    return 0;
}

int test0() {

  std::vector<int32_t> in;
  {
    std::vector<npy::ndarray_len_t> shape;
    std::string type_str;
    npy::LoadArrayFromNumpy("inp0.npy", type_str, shape, in);
  }

  std::vector<int8_t> out(in.size());
  std::vector<int64_t> buffer(in.size());

  for (int i = 0; i < 100000; ++i) {
    auto vv = in;
    log_int_softmax(vv.data(), buffer.data(), out.data(), in.size(),
                               0.2225f);
  }

  std::vector<int32_t> GT;
  {
    std::vector<npy::ndarray_len_t> shape;
    std::string type_str;
    npy::LoadArrayFromNumpy("GT.npy", type_str, shape, GT);
  }

  for (int i = 0; i < GT.size(); ++i) {
    auto diff = GT[i] - (int32_t)out[i];
    if (diff > 0) {
      fprintf(stderr, "diff %d %d %d\n", i, GT[i], (int32_t)out[i]);
    }
  }
  return 0;
}

int main() {
  test0();
}
