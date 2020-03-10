#!/usr/bin/perl

# This script is copyright (c) 2019 by WebMO, LLC, all rights reserved.
# Its use is subject to the license agreement that can be found at the following
# URL:  http://www.webmo.net/license

use lib ".";

$singularity=1;
$container_exec="singularity exec";
#$mopac_path = "/usr/local/mopac2016/MOPAC2016.exe";
$container_path = "/home/hope-singularity/image-files/mopac2016_centos7.sif";

my ($jobNumber, $jobOwner, $queue) = @ARGV;

$require++;
require("globals.cgi");
require("run_parallel.cgi");
&load_interface("interfaces/mopac.int");
&load_interface("queues/$queue/mopac.int") if ($externalBatchQueue);
$require--;

my $input_directory = "$userBase/$jobOwner/$jobNumber";
my ($input_file, $output_file)  = ("$input_directory/input.dat", "$input_directory/output");

print "Executing script: $0\n";

my ($mopac_dir, $input_stub);

($mopac_dir = $mopacPath) =~ s/[^\/]+$//;
($input_stub = $input_file) =~ s/[^\/]+$/input/;
	
# Varying versions of MOPAC use different methods to specify the input file.
# Some use environmental variables, others use the command line, and still
# others read the file from stdin.  For greatest compatability, we send the
# file by all three methods.  If this causes a problem, simply comment out the
# offending methods.
	
# setup enivormental variables for some versions of mopac
$ENV{'FOR005'} = $input_file;
$ENV{'FOR006'} = $output_file.".out";
$ENV{'FOR009'} = $output_file.".res";
$ENV{'FOR010'} = $output_file.".den";
$ENV{'FOR011'} = $output_file.".log";
$ENV{'FOR012'} = $output_file.".arc";
$ENV{'FOR013'} = $output_file.".gpt";
$ENV{'FOR016'} = $output_file.".syb";
$ENV{'FOR018'} = $output_file.".brz";
$ENV{'FOR020'} = $output_file.".ump";
$ENV{'FOR021'} = $output_file.".mep";
$ENV{'SETUP'} = $output_file.".setup";
$ENV{'SHUTDOWN'} = $output_file.".end";

if ($mopacVersion >= 2000)
{
	$ENV{'M2KLIC'} = $mopac_dir;
	$ENV{'MOPAC_LICENSE'} = $mopac_dir;
	$ENV{'LD_LIBRARY_PATH'} .= ":$mopac_dir";
	symlink($input_stub.".out", $output_file.".out");
}

# if we are using PBS, find out which host we are running on
if ($externalBatchQueue)
{
	$host = `hostname`;
	chomp $host;
}
print "Script execution node: $host\n";
	
# change the working directory to scratch, b/c this is where MOPAC creates its temp files
my $jobScratch = "$systemScratch/webmo-$uniqueId/$jobNumber";
unless (-e $jobScratch) {
	mkdir($jobScratch, 0755) || die "Cannot create directory $jobScratch: $!";
}
chdir($jobScratch);

if($mopac_pid = fork)
{
	open(pid, ">$input_directory/pid");
	print pid $mopac_pid;
	close(pid);
}
else
{
	$SIG{'INT'} = 'DEFAULT';
	$SIG{'TERM'} = 'DEFAULT';
	
	# Send the argument on the command line as well, for yet another version of mopac
	my $exec_command;
	if ($mopacVersion >= 2002) {
		chdir($input_directory);
		#workaround for expired MOPAC versions by piping a carraige return into STDIN -- at least the job will run, but the warning message is preserved
		if($singularity) {
			$exec_command = "$container_exec $container_path bash -c 'echo "" | $mopacPath input '";
		}
		else {
			$exec_command = "echo '' | $mopacPath input";
		}
	} 
        else {
		# Open stdin to the input file, for other versions of mopac
		open(STDIN, "<$input_file");
		if($singularity) {
			$exec_command = "$container_exec $container_path $mopacPath $input_stub";
		}
		else {
			$exec_command = "$mopacPath $input_stub";
		}
	}
	print "Executing command: $exec_command\n";

	# Linux gets annoyed if STDOUT and STDERR are not redirected
	open(STDOUT, ">$output_file.stdout");
	open(STDERR, ">$output_file.stderr");
	exec($exec_command);	
	print STDERR "Cannot execute $mopacPath: $!";
		
	close(STDIN);
	close(STDOUT);
	close(STDERR);
	exit(0);

}
waitpid($mopac_pid, 0);
	
# Check for files with the "wrong" name
if (-e $input_stub.".out") { rename($input_stub.".out", $output_file.".out"); }
if (-e $input_stub.".res") { rename($input_stub.".res", $output_file.".res"); }
if (-e $input_stub.".den") { rename($input_stub.".den", $output_file.".den"); }
if (-e $input_stub.".log") { rename($input_stub.".log", $output_file.".log"); }
if (-e $input_stub.".arc") { rename($input_stub.".arc", $output_file.".arc"); }
if (-e $input_stub.".gpt") { rename($input_stub.".gpt", $output_file.".gpt"); }
if (-e $input_stub.".syb") { rename($input_stub.".syb", $output_file.".syb"); }
if (-e $input_stub.".brz") { rename($input_stub.".brz", $output_file.".brz"); }
if (-e $input_stub.".ump") { rename($input_stub.".ump", $output_file.".ump"); }
if (-e $input_stub.".mep") { rename($input_stub.".mep", $output_file.".mep"); }
if (-e $input_stub.".setup") { rename($input_stub.".setup", $output_file.".setup"); }
if (-e $input_stub.".end") { rename($input_stub.".end", $output_file.".end"); }

# Append any text from STDOUT and STDERR to the output file
system("$catPath $output_file.stdout $output_file.stderr >> $output_file.out");
unlink("$output_file.stderr");
