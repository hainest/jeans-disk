#pragma once

#include "tipsy.h"
#include <stdio.h>

typedef struct { FILE* fd; } tipsy_native_stream;

typedef enum { TIPSY_NATIVE_ENCODE, TIPSY_NATIVE_DECODE } tipsy_native_dir;

#ifdef __cplusplus
extern "C" {
#endif

int  tipsy_init_native(tipsy_native_stream*, char const*, tipsy_native_dir);
void tipsy_destroy_native(tipsy_native_stream*);

int tipsy_read_header_native(tipsy_native_stream*, tipsy_header*);
int tipsy_read_gas_native(tipsy_native_stream*, tipsy_header const*, tipsy_gas_data*);
int tipsy_read_dark_native(tipsy_native_stream*, tipsy_header const*, tipsy_dark_data*);
int tipsy_read_star_native(tipsy_native_stream*, tipsy_header const*, tipsy_star_data*);

int tipsy_write_header_native(tipsy_native_stream*, tipsy_header const*);
int tipsy_write_gas_native(tipsy_native_stream*, tipsy_gas_data const*);
int tipsy_write_dark_native(tipsy_native_stream*, tipsy_dark_data const*);
int tipsy_write_star_native(tipsy_native_stream*, tipsy_star_data const*);

#ifdef __cplusplus
}
#endif
