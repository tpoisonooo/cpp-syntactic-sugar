g++ -std=c++14 -g -O0 -c main.cpp
g++ -std=c++14 -g -O0 -c ini_config.cpp

g++ -o main main.o ini_config.o
