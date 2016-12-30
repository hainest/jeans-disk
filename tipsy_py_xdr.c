#include "tipsy.h"
#include "tipsyio_xdr.h"

static tipsy_xdr_stream xdr_stream;

int tipsy_py_init_reader_xdr(char const* filename) {
	return tipsy_init_xdr(&xdr_stream, filename, TIPSY_XDR_DECODE);
}
int tipsy_py_init_writer_xdr(char const* filename) {
	return tipsy_init_xdr(&xdr_stream, filename, TIPSY_XDR_ENCODE);
}
void tipsy_py_destroy_xdr() {
	tipsy_destroy_xdr(&xdr_stream);
}

/****************************************************************************/
int tipsy_py_read_header_xdr(tipsy_header* h) {
	return tipsy_read_header_xdr(&xdr_stream, h);
}
int tipsy_py_read_gas_xdr(tipsy_header const* h, tipsy_gas_data* d) {
	return tipsy_read_gas_xdr(&xdr_stream, h, d);
}
int tipsy_py_read_dark_xdr(tipsy_header const* h, tipsy_dark_data* d) {
	return tipsy_read_dark_xdr(&xdr_stream, h, d);
}
int tipsy_py_read_star_xdr(tipsy_header const* h, tipsy_star_data* d) {
	return tipsy_read_star_xdr(&xdr_stream, h, d);
}

/****************************************************************************/
int tipsy_py_write_header_xdr(tipsy_header* h) {
	return tipsy_write_header_xdr(&xdr_stream, h);
}
int tipsy_py_write_gas_xdr(tipsy_gas_data* d) {
	return tipsy_write_gas_xdr(&xdr_stream, d);
}
int tipsy_py_write_dark_xdr(tipsy_dark_data* d) {
	return tipsy_write_dark_xdr(&xdr_stream, d);
}
int tipsy_py_write_star_xdr(tipsy_star_data* d) {
	return tipsy_write_star_xdr(&xdr_stream, d);
}
