#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
use CGI::Pretty;
use CGI::Carp qw(fatalsToBrowser);
use JSON;

my $cgi = new CGI;
print header('application/json');

if ($cgi->param("action") eq "getparameters") {
	my $parameterset = $cgi->param("parameterset");
	open my $parameterfile, "parameter_files/".$parameterset.".param" or die "Could not open $parameterset.param: $!";
	my @jsonarray;
	while (my $parameterline = <$parameterfile>) {
		my %parameters;
		chomp($parameterline);
		next if $parameterline eq "";
		my ($key, $value) = split("\t", $parameterline);
		$parameters{$key} = $value;
		push(@jsonarray, \%parameters);
	}
	close($parameterfile);
	print encode_json(\@jsonarray);
}

if ($cgi->param("action") eq "getimagelist") {
	open my $fh, "annotation_results/".$cgi->param("imageset")."_".$cgi->param("paramset")."_".$cgi->param("user").".txt";
	my @annotatedfiles = ();
	while (my $resultsline = <$fh>) {
		chomp($resultsline);
		my @temp = split("\t", $resultsline);
		push(@annotatedfiles, $temp[1]);
	}
	my @files = glob( $cgi->param("imageset") . '/*' );
	my @jsonobject;
	foreach my $file (@files) {
		next unless $file =~ /(jpe?g|png|gif)$/i;
		my $escapedfile = quotemeta($file);
		unless (grep (/^$escapedfile$/, @annotatedfiles)) {
			push(@jsonobject, $file);
		}
#		else {print "SKIPPED: $file\n";};
	}
	print encode_json(\@jsonobject);
}

if ($cgi->param("action") eq "annotate") {
	open my $fh, '>>', "annotation_results/".$cgi->param("imageset")."_".$cgi->param("paramset")."_".$cgi->param("user").".txt" or die "Could not open file $!";
	print $fh $cgi->param("annotation"),"\t",$cgi->param("file"),"\n";
	close $fh;
}
