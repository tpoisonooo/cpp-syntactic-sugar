#include "npy.h"
#include <cassert>
#include <cmath>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

static inline int32_t int_polynominal(const int32_t x, const float s) {
  // ax**2 + bx + c
  const float coef0 = 0.35815147;
  const float coef1 = 0.96963238 / coef0;
  const float coef2 = 1.0 / coef0;

  const int32_t b_int = floor(coef1 * s);
  const int32_t c_int = floor(coef2 * s * s);
  return x * (x + b_int) + c_int;
}

static inline int64_t int_exp(int32_t x, float s) {
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
}

static inline float fast_pow2_multiply_3(const int32_t index) {
  assert(index <= 30 && index >= -1);
  static float table[] = {
      1.5f,       3,         6,         12,        24,        48,
      96,         192,       384,       768,       1536,      3072,
      6144,       12288,     24576,     49152,     98304,     196608,
      393216,     786432,    1572864,   3145728,   6291456,   12582912,
      25165824,   50331648,  100663296, 201326592, 402653184, 805306368,
      1610612736, 3221225472};
  return table[index + 1];
}

static inline int32_t find_first_one(int32_t v) {
  int pos = 0;

  if (v > 0xffff) {
    v >>= 16;
    pos += 16;
  }

  if (v > 0xff) {
    v >>= 8;
    pos += 8;
  }

  if (v > 0xf) {
    v >>= 4;
    pos += 4;
  }

  if (v > 0x3) {
    v >>= 2;
    pos += 2;
  }

  if (v > 0x1) {
    v >>= 1;
    pos += 1;
  }

  return pos;
}

int log_int_softmax_inverse_15(int32_t *ptr, int64_t *buffer, int8_t *out,
                               const int len, float scale) {
  int32_t max = ptr[0];
  for (int i = 0; i < len; ++i) {
    if (max < ptr[i]) {
      max = ptr[i];
    }
  }

  int64_t sum = 0;
  for (int i = 0; i < len; ++i) {
    ptr[i] = ptr[i] - max;
    buffer[i] = int_exp(ptr[i], scale);
    sum += buffer[i];
  }

  for (int i = 0; i < len; ++i) {
    ptr[i] = int32_t(sum * 1.f / buffer[i] + 0.5f);
  }

  // log_round
  const int QUANT_MAX = 15;
  for (int i = 0; i < len; ++i) {
    // int32_t val = floor(log2(ptr[i]));
    int32_t val = find_first_one(ptr[i]);
    float big = fast_pow2_multiply_3(val - 1);
    // fprintf(stdout, "val %d\n", val);
    if (ptr[i] >= big) {
      // fprintf(stdout, "big index %d\n", i);
      val += 1;
    }

    if (val > QUANT_MAX) {
      out[i] = -1;
      continue;
    }

    // out[i] = 16 - val;
    out[i] = val;
  }

  return 0;
}

int main() {

  std::vector<int32_t> in;
  {
    std::vector<npy::ndarray_len_t> shape;
    std::string type_str;
    npy::LoadArrayFromNumpy("inpx.npy", type_str, shape, in);
  }

  std::vector<int8_t> out(in.size());
  std::vector<int64_t> buffer(in.size());

  for (int i = 0; i < 100000; ++i) {
    auto vv = in;

    log_int_softmax_inverse_15(vv.data(), buffer.data(), out.data(), in.size(),
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
      return -1;
    }
  }
  return 0;
}
