#pragma once

#include <stddef.h>

typedef struct {
	double       time;
	unsigned int nbodies;
	int	  ndim;
	unsigned int ngas;
	unsigned int ndark;
	unsigned int nstar;
} tipsy_header;

typedef struct {
	float mass;
	float pos[3];
	float vel[3];
	float rho;
	float temp;
	float hsmooth;
	float metals;
	float phi;
} tipsy_gas_particle;

typedef struct {
	float mass;
	float pos[3];
	float vel[3];
	float softening;
	float phi;
} tipsy_dark_particle;

typedef struct {
	float mass;
	float pos[3];
	float vel[3];
	float metals;
	float tform;
	float softening;
	float phi;
} tipsy_star_particle;

typedef struct {
	float* mass;
	float (*pos)[3];
	float (*vel)[3];
	float* rho;
	float* temp;
	float* hsmooth;
	float* metals;
	float* phi;
	size_t size;
} tipsy_gas_data;

typedef struct {
	float* mass;
	float (*pos)[3];
	float (*vel)[3];
	float* soft;
	float* phi;
	size_t size;
} tipsy_dark_data;

typedef struct {
	float* mass;
	float (*pos)[3];
	float (*vel)[3];
	float* metals;
	float* tform;
	float* soft;
	float* phi;
	size_t size;
} tipsy_star_data;
