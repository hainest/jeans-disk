#include "tipsy.h"
#include "tipsyio_err.h"
#include "tipsyio_xdr.h"
#include <errno.h>

/* All XDR routines return one on success and zero, otherwise. */
enum { TIPSY_XDR_FAILURE = 0, TIPSY_XDR_SUCCESS = 1 };

inline static void reset_fd(FILE* fd, size_t offset) {
	int i = fseek(fd, (long)offset, SEEK_SET);
	(void)i;
}

inline static int __tipsy_header(XDR*, tipsy_header*);
inline static int __tipsy_gas(XDR*, tipsy_gas_data*);
inline static int __tipsy_dark(XDR*, tipsy_dark_data*);
inline static int __tipsy_star(XDR*, tipsy_star_data*);

/*************************************************************************************************************/
int tipsy_init_xdr(tipsy_xdr_stream* xdr_stream, char const* filename, tipsy_xdr_dir dir) {
	switch (dir) {
	case TIPSY_XDR_ENCODE:
		xdr_stream->fd = fopen(filename, "wb");
		if (errno != 0) { return errno; }
		xdrstdio_create(&(xdr_stream->xdr), xdr_stream->fd, XDR_ENCODE);
		return 0;
	case TIPSY_XDR_DECODE:
		xdr_stream->fd = fopen(filename, "rb");
		if (errno != 0) { return errno; }
		xdrstdio_create(&(xdr_stream->xdr), xdr_stream->fd, XDR_DECODE);
		return 0;
	default:
		return TIPSY_BAD_XDR_DIR;
	}
}
void tipsy_destroy_xdr(tipsy_xdr_stream* xdr_stream) {
	if (xdr_stream->fd) fclose(xdr_stream->fd);
	xdr_destroy(&(xdr_stream->xdr));
}

/*************************************************************************************************************/
int tipsy_read_header_xdr(tipsy_xdr_stream* xdr_stream, tipsy_header* h) {
	if (!xdr_stream->fd) { return TIPSY_READ_UNOPENED; }
	reset_fd(xdr_stream->fd, 0);
	const int status = __tipsy_header(&(xdr_stream->xdr), h);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_READ : 0;
}
int tipsy_read_gas_xdr(tipsy_xdr_stream* xdr_stream, tipsy_header const* h, tipsy_gas_data* d) {
	(void)h;
	if (!xdr_stream->fd) { return TIPSY_READ_UNOPENED; }
	const size_t offset = sizeof(tipsy_header);
	reset_fd(xdr_stream->fd, offset - sizeof(float));
	const int status = __tipsy_gas(&(xdr_stream->xdr), d);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_READ : 0;
}
int tipsy_read_dark_xdr(tipsy_xdr_stream* xdr_stream, tipsy_header const* h, tipsy_dark_data* d) {
	if (!xdr_stream->fd) { return TIPSY_READ_UNOPENED; }
	const size_t offset = sizeof(tipsy_header) + h->ngas * sizeof(tipsy_gas_particle);
	reset_fd(xdr_stream->fd, offset - sizeof(float));
	const int status = __tipsy_dark(&(xdr_stream->xdr), d);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_READ : 0;
}
int tipsy_read_star_xdr(tipsy_xdr_stream* xdr_stream, tipsy_header const* h, tipsy_star_data* d) {
	if (!xdr_stream->fd) { return TIPSY_READ_UNOPENED; }
	const size_t offset = sizeof(tipsy_header) + h->ngas * sizeof(tipsy_gas_particle) +
			      h->ndark * sizeof(tipsy_dark_particle);
	reset_fd(xdr_stream->fd, offset - sizeof(float));
	const int status = __tipsy_star(&(xdr_stream->xdr), d);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_READ : 0;
}

/*************************************************************************************************************/
int tipsy_write_header_xdr(tipsy_xdr_stream* xdr_stream, tipsy_header const* h) {
	if (!xdr_stream->fd) { return TIPSY_WRITE_UNOPENED; }
	const int status = __tipsy_header(&(xdr_stream->xdr), (tipsy_header*)h);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_WRITE : 0;
}
int tipsy_write_gas_xdr(tipsy_xdr_stream* xdr_stream, tipsy_gas_data const* d) {
	if (!xdr_stream->fd) { return TIPSY_WRITE_UNOPENED; }
	const int status = __tipsy_gas(&(xdr_stream->xdr), (tipsy_gas_data*)d);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_WRITE : 0;
}
int tipsy_write_dark_xdr(tipsy_xdr_stream* xdr_stream, tipsy_dark_data const* d) {
	if (!xdr_stream->fd) { return TIPSY_WRITE_UNOPENED; }
	const int status = __tipsy_dark(&(xdr_stream->xdr), (tipsy_dark_data*)d);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_WRITE : 0;
}
int tipsy_write_star_xdr(tipsy_xdr_stream* xdr_stream, tipsy_star_data const* d) {
	if (!xdr_stream->fd) { return TIPSY_WRITE_UNOPENED; }
	const int status = __tipsy_star(&(xdr_stream->xdr), (tipsy_star_data*)d);
	return (status == TIPSY_XDR_FAILURE) ? TIPSY_BAD_XDR_WRITE : 0;
}

/*************************************************************************************************************/
static int __tipsy_header(XDR* xdr, tipsy_header* h) {
	int status = TIPSY_XDR_SUCCESS;
	status &= xdr_double(xdr, &(h->time));
	status &= xdr_u_int(xdr, &(h->nbodies));
	status &= xdr_int(xdr, &(h->ndim));
	status &= xdr_u_int(xdr, &(h->ngas));
	status &= xdr_u_int(xdr, &(h->ndark));
	status &= xdr_u_int(xdr, &(h->nstar));
	return status;
}

static int __tipsy_gas(XDR* xdr, tipsy_gas_data* d) {
	const size_t size   = d->size;
	int	  status = TIPSY_XDR_SUCCESS;
	for (size_t i = 0; i < size; ++i) {
		status &= xdr_float(xdr, &(d->mass[i]));
		status &= xdr_vector(xdr, (char*)(&(d->pos[i])), 3, sizeof(float), (xdrproc_t)xdr_float);
		status &= xdr_vector(xdr, (char*)(&(d->vel[i])), 3, sizeof(float), (xdrproc_t)xdr_float);
		status &= xdr_float(xdr, &(d->rho[i]));
		status &= xdr_float(xdr, &(d->temp[i]));
		status &= xdr_float(xdr, &(d->hsmooth[i]));
		status &= xdr_float(xdr, &(d->metals[i]));
		status &= xdr_float(xdr, &(d->phi[i]));
		if (status == TIPSY_XDR_FAILURE) break;
	}
	return status;
}

static int __tipsy_dark(XDR* xdr, tipsy_dark_data* d) {
	const size_t size   = d->size;
	int	  status = TIPSY_XDR_SUCCESS;
	for (size_t i = 0; i < size; ++i) {
		status &= xdr_float(xdr, &(d->mass[i]));
		status &= xdr_vector(xdr, (char*)(&(d->pos[i])), 3, sizeof(float), (xdrproc_t)xdr_float);
		status &= xdr_vector(xdr, (char*)(&(d->vel[i])), 3, sizeof(float), (xdrproc_t)xdr_float);
		status &= xdr_float(xdr, &(d->soft[i]));
		status &= xdr_float(xdr, &(d->phi[i]));
		if (status == TIPSY_XDR_FAILURE) break;
	}
	return status;
}

static int __tipsy_star(XDR* xdr, tipsy_star_data* d) {
	const size_t size   = d->size;
	int	  status = TIPSY_XDR_SUCCESS;
	for (size_t i = 0; i < size; ++i) {
		status &= xdr_float(xdr, &(d->mass[i]));
		status &= xdr_vector(xdr, (char*)(&(d->pos[i])), 3, sizeof(float), (xdrproc_t)xdr_float);
		status &= xdr_vector(xdr, (char*)(&(d->vel[i])), 3, sizeof(float), (xdrproc_t)xdr_float);
		status &= xdr_float(xdr, &(d->metals[i]));
		status &= xdr_float(xdr, &(d->tform[i]));
		status &= xdr_float(xdr, &(d->soft[i]));
		status &= xdr_float(xdr, &(d->phi[i]));
		if (status == TIPSY_XDR_FAILURE) break;
	}
	return status;
}
