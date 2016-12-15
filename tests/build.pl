use strict;
use warnings;
use Utilities qw(execute);
use File::Copy qw(copy);

if (! -e '../libtipsy.so') {
	execute(qq(
		cd ..
		make
	));
}

execute(qq(
	cd Gadget3
	perl makeParamFiles.pl
));

execute(qq(
	cd ChaNGa
	perl makeParamFiles.pl
));

# no gas
copy('snap_000.hdf5', 'snap_000.hdf5.tmp');
execute("python3 fix_ics.py --nogas snap_000.hdf5.tmp");
execute("h5repack snap_000.hdf5.tmp Gadget3/nogas/nogas.hdf5");
unlink 'snap_000.hdf5.tmp';

# gas + stars
copy('snap_000.hdf5', 'snap_000.hdf5.tmp');
execute('python3 fix_ics.py snap_000.hdf5.tmp');
execute('h5repack snap_000.hdf5.tmp Gadget3/gas/gas.hdf5');
unlink 'snap_000.hdf5.tmp';

# gas + sfr
copy('snap_000.hdf5', 'snap_000.hdf5.tmp');
execute('python3 fix_ics.py --sfr snap_000.hdf5.tmp');
execute('h5repack snap_000.hdf5.tmp Gadget3/gas+sfr/gas+sfr.hdf5');
unlink 'snap_000.hdf5.tmp';

for my $t ('nogas', 'gas') {
	execute("python3 ../gadget2changa.py --no-param-list Gadget3/$t/$t.hdf5 Gadget3/$t/$t.params ChaNGa/$t");
}

execute("python3 ../gadget2changa.py --no-param-list --generations=6 Gadget3/gas+sfr/gas+sfr.hdf5 Gadget3/gas+sfr/gas+sfr.params ChaNGa/gas+sfr");

