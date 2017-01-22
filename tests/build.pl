use strict;
use warnings;
use Utilities qw(execute);
use File::Copy qw(copy);

die "Usage: $0 input.hdf5\n" if (@ARGV != 1);
my $input_file = $ARGV[0];

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
copy($input_file, "$input_file.tmp");
execute("python3 fix_ics.py --nogas $input_file.tmp");
execute("h5repack $input_file.tmp Gadget3/nogas/nogas.hdf5");
unlink "$input_file.tmp";

# gas + stars
copy($input_file, "$input_file.tmp");
execute('python3 fix_ics.py $input_file.tmp');
execute('h5repack $input_file.tmp Gadget3/gas/gas.hdf5');
unlink "$input_file.tmp";

# gas + sfr
copy($input_file, "$input_file.tmp");
execute('python3 fix_ics.py --sfr $input_file.tmp');
execute('h5repack $input_file.tmp Gadget3/gas+sfr/gas+sfr.hdf5');
unlink "$input_file.tmp";

for my $t ('nogas', 'gas') {
	execute("python3 ../gadget2changa.py --no-param-list Gadget3/$t/$t.hdf5 Gadget3/$t/$t.params ChaNGa/$t");
}

execute("python3 ../gadget2changa.py --no-param-list --generations=6 Gadget3/gas+sfr/gas+sfr.hdf5 Gadget3/gas+sfr/gas+sfr.params ChaNGa/gas+sfr");

