#include <iostream>

template <class Lambda>
void RegisterBenchmark(Lambda&& fn) {
  fprintf(stdout, "first version\n");
}


template<typename X>
void xx(X);

template <class Lambda, class... Args>
void RegisterBenchmark2(Lambda&& fn, Args&&... args) {
  fprintf(stdout, "second version\n");

auto ftmp = fn;
xx(ftmp);
ftmp(1);
 // auto fff = [=](){fn(args...);};
//  auto fff = [&fn, &args...]{fn(args...);};
//  auto hhh = [=]{std::forward<decltype(fn)>(fn)(args...);};
 // RegisterBenchmark(std::move(fff)); 
}

struct FFF {
	int (&fn)(int);
	int arg;

	int operator()() {
		return fn(arg);
	}
};

template <class Lambda, class... Args>
void RegisterBenchmark(Lambda&& fn, Args&&... args) {
  fprintf(stdout, "second version\n");

// Lambda = int(&)(int), Args = int&

// [=]() { }
// int tmpArg = Arg;
// int (??)(int) = Lambda
// auto fff = Lambda; -- > typeof fff == int (*)(int);

// auto gn = fn;
// xx(gn);
  //auto fff = [=, fn=std::forward<Lambda>(fn), ar](){ fn(args...); };
  //auto ggg = [=](){ fn(args...); };

  // no auto decay in g++7.5
  // auto ddd = [=](){ fn(args...); };

  auto fff = [=, gn=std::forward<Lambda>(fn)](){ gn(args...); };

  auto ggg = [=, gn=std::decay_t<Lambda>(fn)](){ gn(args...); };
//  auto ggg = fff;
//  auto fff = [&fn, &args...]{fn(args...);};
//  auto hhh = [=]{std::forward<decltype(fn)>(fn)(args...);};
  RegisterBenchmark(std::move(fff)); 
}


int func(int a) {
  fprintf(stdout, "%d\n", a);
}


int main() {
RegisterBenchmark(func, 12);
return 0;
}
