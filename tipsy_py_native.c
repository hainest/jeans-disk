#include "tipsy.h"
#include "tipsyio_native.h"

static tipsy_native_stream stream;

/****************************************************************************/
int tipsy_py_init_reader_native(char const* filename) {
	return tipsy_init_native(&stream, filename, "rb", TIPSY_NATIVE_DECODE);
}
int tipsy_py_init_writer_native(char const* filename, const char* mode) {
	return tipsy_init_native(&stream, filename, mode, TIPSY_NATIVE_ENCODE);
}
void tipsy_py_destroy_native() {
	tipsy_destroy_native(&stream);
}

/****************************************************************************/
int tipsy_py_read_header_native(tipsy_header* h) {
	return tipsy_read_header_native(&stream, h);
}
int tipsy_py_read_gas_native(tipsy_header const* h, tipsy_gas_data* d) {
	return tipsy_read_gas_native(&stream, h, d);
}
int tipsy_py_read_dark_native(tipsy_header const* h, tipsy_dark_data* d) {
	return tipsy_read_dark_native(&stream, h, d);
}
int tipsy_py_read_star_native(tipsy_header const* h, tipsy_star_data* d) {
	return tipsy_read_star_native(&stream, h, d);
}

/****************************************************************************/
int tipsy_py_write_header_native(tipsy_header* h) {
	return tipsy_write_header_native(&stream, h);
}
int tipsy_py_write_gas_native(tipsy_gas_data* d) {
	return tipsy_write_gas_native(&stream, d);
}
int tipsy_py_write_dark_native(tipsy_dark_data* d) {
	return tipsy_write_dark_native(&stream, d);
}
int tipsy_py_write_star_native(tipsy_star_data* d) {
	return tipsy_write_star_native(&stream, d);
}
