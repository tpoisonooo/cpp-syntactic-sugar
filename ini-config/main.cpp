#include "ini_config.h"
#include <cassert>
#include <memory>

void test_write() {
  std::shared_ptr<ini::Config> pconf = std::make_shared<ini::Config>();

  using ptr_t = std::shared_ptr<ini::Table>;

  {
    ptr_t pt = std::make_shared<ini::Table>();
    pt->append("weight", std::vector<float>({1, 2, 3, 4}));
    pt->append("qweight", -1);
    pt->append("scale_float", 2.2f);
    pt->append("scale_double", 3.3);

    std::string str = pt->stringify();
    fprintf(stdout, "table stringify:\n%s\n", str.c_str());

    pconf->append("conv.0", pt);
  }

  {
    ptr_t pt = std::make_shared<ini::Table>();
    pt->append("weight", std::vector<float>({1, 2, 3, 4}));
    pt->append("qweight", -128);
    pt->append("scale_float", 2.2f);
    pt->append("scale_double", 3.3);

    pconf->append("LayerNorm_66", pt);
  }

  {
    ptr_t pt = std::make_shared<ini::Table>();
    pt->append("weight", std::vector<float>({1, 2, 3, 4}));
    pt->append("qweight", -128);
    pt->append("scale_float", 2.2f);
    pt->append("type", std::string("LayerNorm").c_str());
    pt->append("scale_double", 3.3);

    pconf->append("LayerNorm_68", pt);
  }

  const auto &names = pconf->list_all();
  // for (size_t i = 0; i < names.size(); i++)
  // {
  //     fprintf(stdout, "name %s|", names[i].c_str());
  // }
  fprintf(stdout, "finish");
  assert(3 == names.size());

  pconf->write("quant.ini");
}

void test_read() {
  std::shared_ptr<ini::Config> pconf = std::make_shared<ini::Config>();

  pconf->read("quant.ini");

  const auto &names = pconf->list_all();
  for (size_t i = 0; i < names.size(); i++) {
    fprintf(stdout, "name %s|", names[i].c_str());
  }
  fprintf(stdout, "\n");
  auto ptable = pconf->operator[]("conv.0");
  std::vector<float> weights = ptable->get_list<float>("weight");
  for (auto w : weights) {
    fprintf(stdout, "%f ", w);
  }
  fprintf(stdout, "\n");
  pconf->write("re-quant.ini");
}

int main() {
  test_write();
  test_read();
}
