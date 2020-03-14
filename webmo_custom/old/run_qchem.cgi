#!/usr/bin/perl

# This script is copyright (c) 2019 by WebMO, LLC, all rights reserved.
# Its use is subject to the license agreement that can be found at the following
# URL:  http://www.webmo.net/license

use lib ".";
$singularity=1;
$container_exec="singularity exec";
$container_path="/home/hope-singularity/image-files/qchem5-0_centos-7-6.sif";

my ($jobNumber, $jobOwner, $queue) = @ARGV;

$require++;
require("globals.cgi");
require("run_parallel.cgi");
&load_interface("interfaces/qchem.int");
&load_interface("queues/$queue/qchem.int") if ($externalBatchQueue);
$require--;

my $input_directory = "$userBase/$jobOwner/$jobNumber";
my ($input_file, $output_file)  = ("$input_directory/input.inp", "$input_directory/output.out");

print "Executing script: $0\n";
	
my $jobScratch = "$systemScratch/webmo-$uniqueId/$jobNumber";
print "Creating working directory: $jobScratch\n";
unless (-e $jobScratch) {
	mkdir($jobScratch, 0755) || die "Cannot create directory $jobScratch: $!";
}

$ENV{'QC'}=$qchemBase;
$ENV{'QCAUX'}="$qchemBase/qcaux";
$ENV{'QCSCRATCH'}=$jobScratch;
$ENV{'HOME'}=$jobScratch;

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
	
	# change directory to the job directory for some output files
	chdir($input_directory);
	
	my $np = $nproc > 1 ? "-np $nproc" : "";
	# add the PBS flag for later versions of Q-Chem; if your version
	# of Q-Chem does not understand the -pbs flag, you may need to
	# commment the following line, and modify the parallel.csh script
	# to manually point the the PBS node file (see Q-Chem README.Parallel)
	$np = "-pbs $np" if (	$qchemVersion >= 3.0 &&
							$externalBatchQueue eq 'pbs');
	my $exec_command;
	if (-d "$input_directory/output.chk") {	
		symlink("$input_directory/output.chk", "$jobScratch/output.chk");
		symlink("$input_directory/NBODATA.32", "$jobScratch/output.chk/NBODATA.32");
		symlink("$input_directory/NBODATA.34", "$jobScratch/output.chk/NBODATA.34");
		symlink("$input_directory/NBODATA.36", "$jobScratch/output.chk/NBODATA.36");
		symlink("$input_directory/NBODATA.48", "$jobScratch/output.chk/NBODATA.48");
		symlink("$input_directory/NBODATA.82", "$jobScratch/output.chk/NBODATA.82");
		symlink("$input_directory/NBODATA.84", "$jobScratch/output.chk/NBODATA.84");
		symlink("$input_directory/NBODATA.86", "$jobScratch/output.chk/NBODATA.86");
		symlink("$input_directory/NBODATA.92", "$jobScratch/output.chk/NBODATA.92");
		symlink("$input_directory/NBODATA.94", "$jobScratch/output.chk/NBODATA.94");
		symlink("$input_directory/NBODATA.96", "$jobScratch/output.chk/NBODATA.96");
		
		$exec_command = ". $qchemBase/bin/qchem.setup.sh; $qchemBase/bin/qchem $np input.inp output.out output.chk";
	}
	else {
		$exec_command = ". $qchemBase/bin/qchem.setup.sh; $qchemBase/bin/qchem $np input.inp output.out";
	}
        if($singularity) {
                $exec_command = "$container_exec $container_path bash -c \"$exec_command\" ";
        }
	print "Executing command: $exec_command\n";

	open(STDIN, "<$input_file");
	open(STDOUT, ">$output_file.stdout");
	open(STDERR, ">$output_file.stderr");
	exec($exec_command);
	print STDERR "Cannot execute $qchemBase/bin/qchem: $!";
		
	close(STDIN);
	close(STDOUT);
	close(STDERR);
	exit(0);
}
waitpid($q_pid, 0);

# Append any text from STDOUT and STDERR to the output file
system("$catPath $output_file.stdout $output_file.stderr >> $output_file");
unlink("$output_file.stdout");
unlink("$output_file.stderr");
