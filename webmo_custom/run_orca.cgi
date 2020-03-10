#!/usr/bin/perl

# This script is copyright (c) 2019 by WebMO, LLC, all rights reserved.
# Its use is subject to the license agreement that can be found at the following
# URL:  http://www.webmo.net/license

use lib ".";

$singularity=1;
$container_exec="singularity exec";
$container_path="/home/hope-singularity/image-files/orca.sif";

my ($jobNumber, $jobOwner, $queue) = @ARGV;

$require++;
require("globals.cgi");
require("run_parallel.cgi");
&load_interface("interfaces/orca.int");
&load_interface("queues/$queue/orca.int") if ($externalBatchQueue);
$require--;

my $input_directory = "$userBase/$jobOwner/$jobNumber";
my ($input_file, $output_file)  = ("$input_directory/input.inp", "$input_directory/output.log");

print "Executing script: $0\n";
	
my $jobScratch = "$systemScratch/webmo-$uniqueId/$jobNumber";
print "Creating working directory: $jobScratch\n";
unless (-e $jobScratch) {
	mkdir($jobScratch, 0755) || die "Cannot create directory $jobScratch: $!";
}

$ENV{'PATH'} .= ":$orcaBase";
$ENV{'RSH_COMMAND'} = $serverShell;
$ENV{'NBOEXE'} = "/path/to/nbo6/bin/nbo6.i8.exe"; #update as appropriate if using NBO
$ENV{'GENEXE'} = "/path/to/nbo6/bin/gennbo.i8.exe"; #update as appropriate if using NBO

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

if($q_pid = fork)
{
	open(pid, ">$input_directory/pid");
	print pid $q_pid;
	close(pid);
}
else
{
	$SIG{'INT'} = 'DEFAULT';
	$SIG{'TERM'} = 'DEFAULT';
	
	#copy the input file to the scratch directory
	system("cp $input_file $jobScratch/input.inp");
	#go to the scratch directory
	chdir($jobScratch);

	#copy the nodefile, if needed
	system("$cpPath $node_file input.nodes") if ($nnode > 1);
	
	my $exec_command;
	if ($orcaMPIsetupScript) {
		$exec_command = ". $orcaMPIsetupScript; $orcaBase/orca input.inp";
	} else {
		$exec_command = "$orcaBase/orca input.inp";
	}
        if($singularity) {
                $exec_command = "$container_exec $container_path bash -c \"$exec_command\" ";
        }

	print "Executing command: $exec_command\n";

	open(STDIN, "<$input_file");
	open(STDOUT, ">$output_file");
	open(STDERR, ">&STDOUT");
	exec($exec_command);
	print STDERR "Cannot execute $orcaBase/orca: $!";
		
	close(STDIN);
	close(STDOUT);
	close(STDERR);
	exit(0);
}
waitpid($q_pid, 0);

#convert the orca GBW file to a Molden file for visualization purposes
chdir($jobScratch);
system("$orcaBase/orca_2mkl input -molden");
system("$mvPath input.molden.input $input_directory/output.molden");

#relocate the NBO output files
system("$mvPath $jobScratch/NBODATA.* $input_directory");

