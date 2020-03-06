#!/usr/bin/perl

# This script is copyright (c) 2019 by WebMO, LLC, all rights reserved.
# Its use is subject to the license agreement that can be found at the following
# URL:  http://www.webmo.net/license

use lib ".";
$Singularity=1;
$container_exec="singularity exec";
my ($jobNumber, $jobOwner, $queue) = @ARGV;

$require++;
require("globals.cgi");
require("run_parallel.cgi");
&load_interface("interfaces/gaussian.int");
&load_interface("queues/$queue/gaussian.int") if ($externalBatchQueue);
$require--;

my $input_directory = "$userBase/$jobOwner/$jobNumber";
my ($input_file, $output_file)  = ("$input_directory/input.com", "$input_directory/output.log");

print "Executing script: $0\n";
	
if ($gaussianVersion eq "g94")
{		
	$ENV{'g94root'} = $gaussianRoot;
	$ENV{'G94BASIS'} = $gaussianBasis;
}
elsif ($gaussianVersion eq "g98")
{
	$ENV{'g98root'} = $gaussianRoot;
	$ENV{'G98BASIS'} = $gaussianBasis;
}
elsif ($gaussianVersion eq "g03")
{
	$ENV{'g03root'} = $gaussianRoot;
	$ENV{'G03BASIS'} = $gaussianBasis;
}
elsif ($gaussianVersion eq "g09")
{
	$ENV{'g09root'} = $gaussianRoot;
	$ENV{'G09BASIS'} = $gaussianBasis;
}
elsif ($gaussianVersion eq "g16")
{
	$ENV{'g16root'} = $gaussianRoot;
	$ENV{'G16BASIS'} = $gaussianBasis;
}
elsif ($gaussianVersion eq "gdv")
{
	$ENV{'gdvroot'} = $gaussianRoot;
	$ENV{'GDVBASIS'} = $gaussianBasis;
}

my $jobScratch = "$systemScratch/webmo-$uniqueId/$jobNumber";
print "Creating working directory: $jobScratch\n";
unless (-e $jobScratch) {
	mkdir($jobScratch, 0755) || die "Cannot create directory $jobScratch: $!";
}

$ENV{'GAUSS_SCRDIR'} = $jobScratch;
$ENV{'GAUSS_EXEDIR'} = $GAUSS_EXEDIR;
$ENV{'GAUSS_ARCHDIR'} = $GAUSS_ARCHDIR;
$ENV{'GMAIN'} = $GMAIN;
$ENV{'PATH'} = $ENV{'PATH'}.":".$ENV{'GAUSS_EXEDIR'};
$ENV{'LD_LIBRARY_PATH'} = $LD_LIBRARY_PATH;

# if we are using PBS, find out which host we are running on
if ($externalBatchQueue)
{
	$host = `hostname`;
	chomp $host;
}
print "Script execution node: $host\n";

#parallel job support
my (@node_list, @unique_nodes, %ppn, $nnode, $nproc, $node_file);
&get_nodefile_info($input_directory,\@node_list, \@unique_nodes, \%ppn, \$nnode, \$nproc, \$node_file);
print "Job execution node(s): ", join(' ', @node_list), "\n";

if($g_pid = fork)
{
	open(pid, ">$input_directory/pid");
	print pid $g_pid;
	close(pid);
	
}
else
{
	$SIG{'INT'} = 'DEFAULT';
	$SIG{'TERM'} = 'DEFAULT';
	
	# change directory to the job directory for some output files
	chdir($input_directory);
	
	my $exec_command;	
	if ($nnode > 1 && $gaussianVersion eq 'g03')
	{
		$ENV{'GAUSS_LFLAGS'}="-nodelist \"@unique_nodes\"";
		$exec_command = "$gaussianBase/${gaussianVersion}l";
	}
	elsif ($nnode > 1)
	{
		#for g09/g16, add the %LindaWorkers to the input file
		my $lindaWorkers="%LindaWorkers=".join(',', @unique_nodes);
		system("$mvPath $input_file $input_file.000; echo $lindaWorkers | cat - $input_file.000 > $input_file; $rmPath $input_file.000");
		$exec_command = "$gaussianBase/$gaussianVersion";
	}
	elsif($Singularity){
		$container_path = "/home/hope-singularity/image-files/g16.sif";
		$exec_command = "$container_exec $container_path $gaussianBase/$gaussianVersion";
	}
	else
	{
		$exec_command = "$gaussianBase/$gaussianVersion";
	}
	print "Executing command: $exec_command\n";
	
	open(STDIN, "<$input_file");
	open(STDOUT, ">$output_file");
	open(STDERR, ">&STDOUT");
	exec($exec_command);
	print STDERR "Cannot execute $gaussianBase/$gaussianVersion: $!";
	
	close(STDIN);
	close(STDOUT);
	close(STDERR);
	exit(0);

}
waitpid($g_pid, 0);
