use strict;
use warnings;
use File::Copy qw(copy);
use Getopt::Long qw(GetOptions);
use lib '..';
use Utilities qw(execute);

my $njobs = 2;
GetOptions('njobs=i' => \$njobs) or exit;

my $header = qq(
OPT	+=  -DUNEQUALSOFTENINGS
OPT	+=  -DMULTIPLEDOMAINS=64
OPT	+=  -DTOPNODEFACTOR=3.0
OPT	+=  -DPEANOHILBERT
OPT	+=  -DWALLCLOCK
OPT	+=  -DMYSORT
OPT	+=  -DDOUBLEPRECISION
OPT	+=  -DNO_ISEND_IRECV_IN_DOMAIN
OPT	+=  -DFIX_PATHSCALE_MPI_STATUS_IGNORE_BUG
OPT	+=  -DOUTPUTPOTENTIAL
OPT	+=  -DHAVE_HDF5
);

sub build() {
	execute("cd src; make clean; make -j$njobs");
}

open my $fdOut, '>', 'src/gadget.make' or die;
print $fdOut $header;
close $fdOut;
build();
copy('src/Gadget3', 'nogas/') or die;
copy('src/Gadget3', 'gas/') or die;

open $fdOut, '>', 'src/gadget.make' or die;
print $fdOut qq(
$header
OPT	+=  -DSFR
OPT	+=  -DCOOLING
OPT	+=  -DGENERATIONS=6
OPT	+=  -DMOREPARAMS
OPT	+=  -DSTELLARAGE
);
close $fdOut;
build();
copy('src/Gadget3', 'gas+sfr/') or die;

