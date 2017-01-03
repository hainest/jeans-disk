CC       = gcc
CCSTD    = -std=c99
CXX      = g++
CXXSTD   = -std=c++14
WFLAGS   = -Wall -Wextra -Wconversion -Wshadow -Wsign-compare
OPTIMIZE = -m64 -O3 -march=native -mfpmath=sse -DNDEBUG

SRCS  = tipsy_py_xdr.c tipsyio_xdr.c tipsyio_err.c tipsyio_native.c tipsy_py_native.c
OBJS := $(patsubst %.c, %.o, $(SRCS))
LIB   = libtipsy.so

debug: SANITIZER := address
debug: LDFLAGS	 := -fuse-ld=gold -fsanitize=$(SANITIZER)
debug: OPTIMIZE  := -O0 -g -fno-omit-frame-pointer -fsanitize=$(SANITIZER)
debug: all

.DEFAULT_GOAL := all

.PHONY: all
all: $(LIB)

$(LIB): $(OBJS)
	@ echo Building shared library '$@'...
	@ $(CC) -shared -Wl,-soname,$(LIB) $(LDFLAGS) -o $@ $^

%.o: %.c
	@ echo Compiling $<...
	@ $(CC) $(CCSTD) $(OPTIMIZE) $(WFLAGS) $(CFLAGS) -fPIC -c $< -o $@

$(TEST_EXEC): $(TEST_OBJS) tipsyio_xdr.o tipsyio_err.o
	@ $(CXX) $(LDFLAGS) $^ -o $@

.PHONY: dist
dist:
	@ tar -zc --exclude='*.hdf5' --exclude='*.tipsy' -f g2c.tar.gz $(SRCS) *.h *.py Makefile tests

.PHONY: clean
clean:
	@ echo Cleaning...
	@ $(RM) $(OBJS) $(TEST_OBJS) *.pyc

.PHONY: dist-clean
dist-clean: clean
	@ rm -rf $(LIB) $(TEST_EXEC) __pycache__
