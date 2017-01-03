#include "tipsyio_native.h"
#include "tipsyio_err.h"
#include <errno.h>

inline static void reset_fd(FILE* fd, size_t offset) {
	int i = fseek(fd, (long)offset, SEEK_SET);
	(void)i;
}

/*************************************************************************************************************/
int tipsy_init_native(tipsy_native_stream* stream, char const* filename, char const* mode, tipsy_native_dir dir) {
	switch (dir) {
	case TIPSY_NATIVE_ENCODE:
		stream->fd = fopen(filename, mode);
		if (errno != 0) { return errno; }
		return 0;
	case TIPSY_NATIVE_DECODE:
		stream->fd = fopen(filename, mode);
		if (errno != 0) { return errno; }
		return 0;
	default:
		return TIPSY_BAD_NATIVE_DIR;
	}
}
void tipsy_destroy_native(tipsy_native_stream* stream) {
	if (stream->fd) fclose(stream->fd);
}

/*************************************************************************************************************/
int tipsy_read_header_native(tipsy_native_stream* stream, tipsy_header* h) {
	if (!stream->fd) { return TIPSY_READ_UNOPENED; }
	reset_fd(stream->fd, 0);
	if (fread(h, sizeof(tipsy_header), 1, stream->fd) != 1) { return errno; }
	return 0;
}
int tipsy_read_gas_native(tipsy_native_stream* stream, tipsy_header const* h, tipsy_gas_data* d) {
	(void)h;
	if (!stream->fd) { return TIPSY_READ_UNOPENED; }
	const size_t offset = sizeof(tipsy_header);
	reset_fd(stream->fd, offset);
	tipsy_gas_particle p;
	const size_t       size = d->size;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_gas_particle), 1, stream->fd) != 1) { return errno; }
		d->mass[i]    = p.mass;
		d->pos[i][0]  = p.pos[0];
		d->pos[i][1]  = p.pos[1];
		d->pos[i][2]  = p.pos[2];
		d->vel[i][0]  = p.vel[0];
		d->vel[i][1]  = p.vel[1];
		d->vel[i][2]  = p.vel[2];
		d->rho[i]     = p.rho;
		d->temp[i]    = p.temp;
		d->hsmooth[i] = p.hsmooth;
		d->metals[i]  = p.metals;
		d->phi[i]     = p.phi;
	}
	return 0;
}
int tipsy_read_dark_native(tipsy_native_stream* stream, tipsy_header const* h, tipsy_dark_data* d) {
	if (!stream->fd) { return TIPSY_READ_UNOPENED; }
	const size_t offset = sizeof(tipsy_header) + h->ngas * sizeof(tipsy_gas_particle);
	reset_fd(stream->fd, offset);
	const size_t	size = d->size;
	tipsy_dark_particle p;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_dark_particle), 1, stream->fd) != 1) { return errno; }
		d->mass[i]   = p.mass;
		d->pos[i][0] = p.pos[0];
		d->pos[i][1] = p.pos[1];
		d->pos[i][2] = p.pos[2];
		d->vel[i][0] = p.vel[0];
		d->vel[i][1] = p.vel[1];
		d->vel[i][2] = p.vel[2];
		d->soft[i]   = p.softening;
		d->phi[i]    = p.phi;
	}
	return 0;
}
int tipsy_read_star_native(tipsy_native_stream* stream, tipsy_header const* h, tipsy_star_data* d) {
	if (!stream->fd) { return TIPSY_READ_UNOPENED; }
	const size_t offset = sizeof(tipsy_header) + h->ngas * sizeof(tipsy_gas_particle) +
			      h->ndark * sizeof(tipsy_dark_particle);
	reset_fd(stream->fd, offset);
	tipsy_star_particle p;
	const size_t	size = d->size;
	for (size_t i = 0; i < size; ++i) {
		if (fread(&p, sizeof(tipsy_star_particle), 1, stream->fd) != 1) { return errno; }
		d->mass[i]   = p.mass;
		d->pos[i][0] = p.pos[0];
		d->pos[i][1] = p.pos[1];
		d->pos[i][2] = p.pos[2];
		d->vel[i][0] = p.vel[0];
		d->vel[i][1] = p.vel[1];
		d->vel[i][2] = p.vel[2];
		d->metals[i] = p.metals;
		d->tform[i]  = p.tform;
		d->soft[i]   = p.softening;
		d->phi[i]    = p.phi;
	}
	return 0;
}

/*************************************************************************************************************/
int tipsy_write_header_native(tipsy_native_stream* stream, tipsy_header const* h) {
	if (!stream->fd) { return TIPSY_WRITE_UNOPENED; }
	if (fwrite(h, sizeof(tipsy_header), 1, stream->fd) != 1) { return errno; }
	return 0;
}
int tipsy_write_gas_native(tipsy_native_stream* stream, tipsy_gas_data const* d) {
	if (!stream->fd) { return TIPSY_WRITE_UNOPENED; }
	tipsy_gas_particle p;
	const size_t       size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass    = d->mass[i];
		p.pos[0]  = d->pos[i][0];
		p.pos[1]  = d->pos[i][1];
		p.pos[2]  = d->pos[i][2];
		p.vel[0]  = d->vel[i][0];
		p.vel[1]  = d->vel[i][1];
		p.vel[2]  = d->vel[i][2];
		p.rho     = d->rho[i];
		p.temp    = d->temp[i];
		p.hsmooth = d->hsmooth[i];
		p.metals  = d->metals[i];
		p.phi     = d->phi[i];
		if (fwrite(&p, sizeof(tipsy_gas_particle), 1, stream->fd) != 1) { return errno; }
	}
	return 0;
}
int tipsy_write_dark_native(tipsy_native_stream* stream, tipsy_dark_data const* d) {
	if (!stream->fd) { return TIPSY_WRITE_UNOPENED; }
	tipsy_dark_particle p;
	const size_t	size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = d->mass[i];
		p.pos[0]    = d->pos[i][0];
		p.pos[1]    = d->pos[i][1];
		p.pos[2]    = d->pos[i][2];
		p.vel[0]    = d->vel[i][0];
		p.vel[1]    = d->vel[i][1];
		p.vel[2]    = d->vel[i][2];
		p.softening = d->soft[i];
		p.phi       = d->phi[i];
		if (fwrite(&p, sizeof(tipsy_dark_particle), 1, stream->fd) != 1) { return errno; }
	}
	return 0;
}
int tipsy_write_star_native(tipsy_native_stream* stream, tipsy_star_data const* d) {
	if (!stream->fd) { return TIPSY_WRITE_UNOPENED; }
	tipsy_star_particle p;
	const size_t	size = d->size;
	for (size_t i = 0; i < size; ++i) {
		p.mass      = d->mass[i];
		p.pos[0]    = d->pos[i][0];
		p.pos[1]    = d->pos[i][1];
		p.pos[2]    = d->pos[i][2];
		p.vel[0]    = d->vel[i][0];
		p.vel[1]    = d->vel[i][1];
		p.vel[2]    = d->vel[i][2];
		p.metals    = d->metals[i];
		p.tform     = d->tform[i];
		p.softening = d->soft[i];
		p.phi       = d->phi[i];
		if (fwrite(&p, sizeof(tipsy_star_particle), 1, stream->fd) != 1) { return errno; }
	}
	return 0;
}
