#include <iostream>
#include <fstream>

struct header {
	double time;
	int nbodies;
	int ndim;
	int nsph;
	int ndark;
	int nstar;
};

std::ostream& operator<<(std::ostream &o, header const& h) {
	o << "time = " << h.time << '\n' << "nbodies = " << h.nbodies << '\n'
		<< "ndim = " << h.ndim << '\n' << "nsph = " << h.nsph << '\n'
		<< "ndark = " << h.ndark << '\n' << "nstar = " << h.nstar << '\n';
	return o;
}

struct dark_particle {
	float mass;
	float pos[3];
	float vel[3];
	float eps;
	float phi;
};

std::ostream& operator<<(std::ostream &o, dark_particle const& p) {
	o << p.mass << ' ' << '{' << p.pos[0] << ',' << p.pos[1] << ',' << p.pos[2] << '}';
	return o;
}

int main() {
	std::ifstream fin {
			"/home/tim/Projects/OortLimit/vertical_oscillations/200/snap_200_000.tipsy",
			std::ios::binary };

	if (!fin) {
		std::cerr << "Bad file\n";
		return -1;
	}

	header h;
	fin.read(reinterpret_cast<char*>(&h), sizeof(header));
	std::cout << h << std::endl;

	dark_particle p[10];
	fin.read(reinterpret_cast<char*>(p), 10*sizeof(dark_particle));

	for (auto const& e : p) {
		std::cout << e << std::endl;
	}
}
