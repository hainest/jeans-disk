CC       = gcc
CCSTD    = -std=c99
CXX      = g++
CXXSTD   = -std=c++14
WFLAGS   = -Wall -Wextra -Wconversion -Wshadow
OPTIMIZE = -m64 -O3 -march=native -mfpmath=sse -DNDEBUG

SRCS  = tipsyio.c
OBJS := $(patsubst %.c, %.o, $(SRCS))
LIB   = libtipsy.so

TEST_SRCS := test.cpp
TEST_OBJS := $(patsubst %.cpp, %.o, $(TEST_SRCS))
TEST_EXEC := g2c

.DEFAULT_GOAL := all

.PHONY: all
all: $(LIB)

$(LIB): $(OBJS)
	@ echo Building shared library '$@'...
	@ $(CC) -shared -Wl,-soname,$(LIB) -o $@ $^

%.o: %.c
	@ echo Compiling $<...
	@ $(CC) $(CCSTD) $(OPTIMIZE) $(WFLAGS) $(CFLAGS) -fPIC -c $< -o $@

%.o: %.cpp
	@ echo Compiling $<...
	@ $(CXX) $(CXXSTD) $(OPTIMIZE) $(WFLAGS) $(CFLAGS) -c $< -o $@

.PHONY: test
$(TEST_EXEC): $(TEST_OBJS) tipsyio.o
	@ $(CXX) $^ -o $@

.PHONY: dist
dist:
	@ tar -zc --exclude='*.hdf5' --exclude='*.tipsy' -f g2c.tar.gz $(SRCS) test.cpp *.h *.py Makefile tests

.PHONY: clean
clean:
	@ echo Cleaning...
	@ $(RM) $(OBJS) $(TEST_OBJS) *.pyc

.PHONY: dist-clean
dist-clean: clean
	@ rm -rf $(LIB) __pycache__
