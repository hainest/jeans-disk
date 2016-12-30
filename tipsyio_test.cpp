#include <iostream>
#include <cstdio>
#include <fstream>
#include "tipsy.h"

std::ostream& operator<<(std::ostream &o, tipsy_dark_particle const& p) {
	o << '[' << p.pos[0] << ',' << p.pos[1] << ',' << p.pos[2] << ']';
	return o;
}

std::ostream& operator<<(std::ostream &o, tipsy_star_particle const& p) {
	o << '[' << p.pos[0] << ',' << p.pos[1] << ',' << p.pos[2] << ']';
	return o;
}

std::ostream& operator<<(std::ostream &o, tipsy_gas_particle const& p) {
	o << '[' << p.pos[0] << ',' << p.pos[1] << ',' << p.pos[2] << ']';
	return o;
}

std::ostream& operator<<(std::ostream &o, tipsy_header const& h) {
	o << "time = " << h.time << '\n' << "nbodies = " << h.nbodies << '\n'
		<< "ndim = " << h.ndim << '\n' << "ngas = " << h.ngas << '\n'
		<< "ndark = " << h.ndark << '\n' << "nstar = " << h.nstar << '\n';
	return o;
}

int main(int argc, const char* argv[]) {
	std::string filename{"ChaNGa/testdisk.1M.tipsy"};

	if (argc > 2) {
		std::cerr << "Usage: " << argv[0] << " [input]\n";
		return -1;
	}

	if (argc == 2) {
		filename = argv[1];
	}

	std::ifstream fin { filename, std::ios::binary };

	if (!fin) {
		std::cerr << "Bad file\n";
		return -1;
	}

	tipsy_header h;
	fin.read(reinterpret_cast<char*>(&h), sizeof(tipsy_header));
	std::cout << h << std::endl;

	tipsy_gas_particle p[5];
	fin.read(reinterpret_cast<char*>(p), 5*sizeof(tipsy_gas_particle));
	std::cout << "Gas particles:\n";
	for (auto const& e : p) {
		std::cout << e << std::endl;
	}
	std::cout << "\n\n";

	fin.seekg(0); // rewind
	fin.seekg(sizeof(tipsy_header) + h.ngas * sizeof(tipsy_gas_particle) + h.ndark * sizeof(tipsy_dark_particle), std::ios_base::cur);

	tipsy_star_particle stars[5];
	fin.read(reinterpret_cast<char*>(stars), 5*sizeof(tipsy_star_particle));
	for (auto const& e : stars) {
		std::cout << e << std::endl;
	}
}
