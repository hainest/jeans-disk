#pragma once

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
	TIPSY_READ_UNOPENED  = 0x10001, /* Read from unopened file */
	TIPSY_WRITE_UNOPENED = 0x10002, /* Write to unopened file */
	TIPSY_BAD_XDR_DIR    = 0x10003, /* Invalid XDR direction flag */
	TIPSY_BAD_XDR_READ   = 0x10004, /* Bad read on XDR stream */
	TIPSY_BAD_XDR_WRITE  = 0x10005, /* Bad write on XDR stream */
	TIPSY_BAD_NATIVE_DIR = 0x10006  /* Invalid native direction flag */
} tipsy_error_t;

char const* tipsy_strerror(tipsy_error_t);

#ifdef __cplusplus
}
#endif
