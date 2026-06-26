# C/C++ Adapter

The C/C++ adapter detects C and C++ projects and generates reproduction plans.

## Detection

Files detected:
- `CMakeLists.txt`, `Makefile`, `configure`, `meson.build`
- `*.c`, `*.cpp`, `*.cxx`, `*.cc`, `*.h`, `*.hpp`, `src/*.c`, `src/*.cpp`

## Planning

CMake projects:
- Configure: `cmake -S . -B build`
- Build: `cmake --build build`
- Test: `cd build && ctest --output-on-failure`

Makefile projects:
- Build: `make`
- Test: `make test`

## Runtime

Requires: `g++`, `gcc`, `clang++`, or `clang`

Support level: **execute-if-runtime-present**

## Limitations

- C/C++ compiler must be installed separately
- Build process varies by project
- Some projects may require specific libraries
