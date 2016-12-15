use strict;
use warnings;
use File::Copy qw(copy);
use Getopt::Long qw(GetOptions);

sub execute($) {
	my $cmd = shift;
	system($cmd);
	use Carp qw(croak);
	croak "\n\nError executing \n\t'$cmd'\n\n" if ( ( $? >> 8 ) != 0 || $? == -1 || ( $? & 127 ) != 0 );
}

my ($charm, $changa, $clean, $smp, $njobs ) = ( 1, 1, 0 , 1, 2);
GetOptions(
	'charm!'    => \$charm,
	'changa!'   => \$changa,
	'clean'     => \$clean,
	'smp!'		=> \$smp,
	'njobs=i'	=> \$njobs
) or exit;
$smp  = ($smp) ? 'smp' : '';

if($clean && !$changa && !$charm) {
	&clean_charm();
	&clean_changa();
}

if ($charm) {
	&clean_charm() if ($clean);
	execute( "
		cd src/charm
		./build ChaNGa net-linux-x86_64 $smp --enable-lbuserdata -j$njobs -optimize
	" );
}

if ($changa) {
	&clean_changa() if ($clean);
	
	execute("cd src/changa; ./configure; make depends; make -j$njobs");
	copy('src/changa/ChaNGa', 'nogas/') or die;
	copy('src/changa/charmrun', 'nogas/') or die;
	
	copy('src/changa/ChaNGa', 'gas/') or die;
	copy('src/changa/charmrun', 'gas/') or die;
	
	execute("cd src/changa; make clean; ./configure --enable-cooling=cosmo; make -j$njobs");
	copy('src/changa/ChaNGa', 'gas+sfr/') or die;
	copy('src/changa/charmrun', 'gas+sfr/') or die;
}

sub clean_charm() {
	execute( "
		cd src/charm
		rm -rf bin include lib lib_so tmp VERSION net-linux*
	" );
}
sub clean_changa() {
	execute( "
		cd src/changa
		rm -f *.a *.o config.status Makefile.dep Makefile cuda.mk ChaNGa charmrun
	" );	
}
