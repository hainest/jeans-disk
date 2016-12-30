#include "tipsyio_err.h"
#include <string.h>

char const* tipsy_strerror(tipsy_error_t err) {
	switch (err) {
	case TIPSY_READ_UNOPENED:
		return "Attempt to read from unopened file";
	case TIPSY_WRITE_UNOPENED:
		return "Attempt to write to unopened file";
	case TIPSY_BAD_XDR_DIR:
		return "Invalid XDR direction flag";
	case TIPSY_BAD_XDR_READ:
		return "XDR read failed";
	case TIPSY_BAD_XDR_WRITE:
		return "XDR write failed";
	case TIPSY_BAD_NATIVE_DIR:
		return "Invalid native direction flag";
	default:
		// It's a system error
		return strerror((int)err);
	}
}
