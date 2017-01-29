use strict;
use warnings;
use File::Copy qw(copy);
use Getopt::Long qw(GetOptions);
use lib '..';
use Utilities qw(execute);
use Pod::Usage;

my %simd_decode = (
	'sse2' => '--enable-sse2',
	'avx'  => '--enable-avx',
	'generic' => ''
);

my %args = (
	'cuda' 		=> 0,
	'charm' 	=> 1,
	'charm_target' => 'net-linux-x86_64',
	'changa' 	=> 1,
	'clean' 	=> 0,
	'smp'		=> 1,
	'float' 	=> 0,
	'njobs' 	=> 2,
	'hex' 		=> 1,
	'simd' 		=> 'generic',
	'help' 		=> 0
);

GetOptions(\%args,
	'cuda!', 'charm!', 'changa!', 'clean!', 'smp!',
	'float!', 'njobs=i', 'hex!', 'simd=s', 'help',
	'charm_target=s'
) or pod2usage(2);

pod2usage( -exitval => 0, -verbose => 1 ) if $args{'help'};
if (!exists $simd_decode{$args{'simd'}}) {
	print "Unknown simd type: $args{'simd'}\n";
	pod2usage(-exitval => 0);
}

if($args{'clean'} && !$args{'changa'} && !$args{'charm'}) {
	&clean_charm();
	&clean_changa();
}

if ($args{'charm'}) {
	&clean_charm() if ($args{'clean'});
	my $cuda = ($args{'cuda'}) ? 'cuda' : '';
	my $smp = ($args{'smp'}) ? 'smp' : '';
	execute( "
		cd src/charm
		./build ChaNGa $args{'charm_target'} $smp $cuda --enable-lbuserdata --with-production -j$args{'njobs'} -optimize
	" );
}

if ($args{'changa'}) {
	&clean_changa() if ($args{'clean'});
	
	my $cuda = ($args{'cuda'}) ? "--with-cuda" : '';
	my $float = ($args{'float'}) ? '--enable-float' : '';
	my $hex = ($args{'hex'}) ? '' : '--disable-hexadecapole';
	my $simd = $simd_decode{$args{'simd'}};
	
	execute("
		cd src/changa
		./configure $cuda $float $hex $simd
		make depends
		make -j$args{'njobs'}
	");
	copy('src/changa/ChaNGa', 'nogas/') or die;
	copy('src/changa/charmrun', 'nogas/') or die;
	chmod(0755, 'nogas/ChaNGa', 'nogas/charmrun');
	
	copy('src/changa/ChaNGa', 'gas/') or die;
	copy('src/changa/charmrun', 'gas/') or die;
	chmod(0755, 'gas/ChaNGa', 'gas/charmrun');
	
	execute("
        cd src/changa
        make clean
        ./configure --enable-cooling=cosmo $cuda $float $hex $simd
        make -j$args{'njobs'}
    ");
	copy('src/changa/ChaNGa', 'gas+sfr/') or die;
	copy('src/changa/charmrun', 'gas+sfr/') or die;
	chmod(0755, 'gas+sfr/ChaNGa', 'gas+sfr/charmrun');
}

sub clean_charm() {
	execute( "
		cd src/charm
		rm -rf bin include lib lib_so tmp VERSION $args{'charm_target'}
	" );
}
sub clean_changa() {
	execute( "
		cd src/changa
		rm -f *.a *.o config.status Makefile.dep Makefile cuda.mk ChaNGa charmrun
	" );	
}

__END__
 
=head1 NAME
 
charm++ and ChaNGa builder
 
=head1 SYNOPSIS
 
build [options]
 
 Options:
   --cuda          Enable CUDA (default: no)
   --charm         Build charm++ (default: yes)
   --charm_target  Target architecture for charm++ (default: net-linux-x86_64)
   --changa        Build ChaNGa (default: yes)
   --clean         Clean before building (default: yes)
   --smp           Use SMP (default: yes)
   --float         Use single-precision (default: no)
   --njobs         Number of make jobs (default: 2)
   --hex           Use hexadecapole (default: yes)
   --simd          Use SIMD [generic, sse2, avx] (default: generic)
   --help          Print this help message
=cut

