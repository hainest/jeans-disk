#pragma once

#include <rpc/xdr.h>

typedef enum { TIPSY_XDR_ENCODE, TIPSY_XDR_DECODE } tipsy_xdr_dir;

typedef struct {
	XDR   xdr;
	FILE* fd;
} tipsy_xdr_stream;

#ifdef __cplusplus
extern "C" {
#endif

int  tipsy_init_xdr(tipsy_xdr_stream*, char const*, tipsy_xdr_dir);
void tipsy_destroy_xdr(tipsy_xdr_stream*);

int tipsy_read_header_xdr(tipsy_xdr_stream*, tipsy_header*);
int tipsy_read_gas_xdr(tipsy_xdr_stream*, tipsy_header const*, tipsy_gas_data*);
int tipsy_read_dark_xdr(tipsy_xdr_stream*, tipsy_header const*, tipsy_dark_data*);
int tipsy_read_star_xdr(tipsy_xdr_stream*, tipsy_header const*, tipsy_star_data*);

int tipsy_write_header_xdr(tipsy_xdr_stream*, tipsy_header const* h);
int tipsy_write_gas_xdr(tipsy_xdr_stream*, tipsy_gas_data const*);
int tipsy_write_dark_xdr(tipsy_xdr_stream*, tipsy_dark_data const*);
int tipsy_write_star_xdr(tipsy_xdr_stream*, tipsy_star_data const*);

#ifdef __cplusplus
}
#endif
