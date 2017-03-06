#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
use CGI::Pretty;
use CGI::Carp qw(fatalsToBrowser);
use JSON;
use File::Basename;
use lib dirname(__FILE__);
use RapidAnnotatorConfig;

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
	my @jsonobject;
	if (-e "image_files/" . $cgi->param("imageset") . '.playlist') {
		open my $playlistfile, "image_files/" . $cgi->param("imageset") . '.playlist';
		while (my $playlistline = <$playlistfile>) {
			$playlistline =~ s/(.*?)#.*/$1/;
			chomp($playlistline);
			next if ($playlistline eq '');

			my $regex_filename = qr/(\d{4}\-\d{2}\-\d{2}_[^\s\t]+)/;
			my $regex_time = qr/(?:(?:(\d+):)?(\d+):)?(\d+)/;
			my $regex = qr/.*$regex_filename(?:[\s\t]+$regex_time(?:\-$regex_time)?)?[\s\t]*(.*)/;

			# $1: file name
			# $2: start hour
			# $3: start minute
			# $4: start second
			# $5: end hour
			# $6: end minute
			# $7: end second
			# $8: comment

			next if (!($playlistline =~ $regex));

			my $starttime;
			my $endtime;
			my $filename = $1;
			if (($2 or $3 or $4) and ($5 or $6 or $7)) {
				$starttime = $2 * 3600 + $3 * 60 + $4;
				$endtime = $5 * 3600 + $6 * 60 + $7;
			} elsif ($2 or $3 or $4) {
				$starttime = $2 * 3600 + $3 * 60 + $4 - 30;
				$endtime = $starttime + 60;
                        } else {
				$starttime = 0;
				$endtime = $endtime + 30;
                        }
			$starttime = 0 if (!($starttime >= 0));
			$endtime = $starttime + 30 unless (defined $starttime && defined $endtime && $endtime > $starttime);
			my $url = RapidAnnotatorConfig::getVideoURL($filename, $starttime, $endtime);
			my $name = $filename . "," . $starttime . "," . $endtime;
			my $escapedname = quotemeta($name);
                        unless (grep (/^$escapedname$/, @annotatedfiles)) {
                                push(@jsonobject, 'video' . "\t" . $name . "\t" . $url . "\t" . $starttime . "\t" . $endtime);
                        }
		}
		close $playlistfile;
	} else {
		my @files = glob( "image_files/" . $cgi->param("imageset") . '/*' );
		foreach my $file (@files) {
			$file = substr($file, length("image_files/"));
			next unless $file =~ /(jpe?g|png|gif)$/i;
			my $escapedfile = quotemeta($file);
			unless (grep (/^$escapedfile$/, @annotatedfiles)) {
				push(@jsonobject, $file);
			}
#		else {print "SKIPPED: $file\n";};
		}
	}
	print encode_json(\@jsonobject);
}

if ($cgi->param("action") eq "annotate") {
	open my $fh, '>>', "annotation_results/".$cgi->param("imageset")."_".$cgi->param("paramset")."_".$cgi->param("user").".txt" or die "Could not open file $!";
	if (defined $cgi->param("time")) {
		printf $fh "%s\t%s\t%.3f\n", $cgi->param("annotation"),$cgi->param("file"),$cgi->param("time");
	} else {
		printf $fh "%s\t%s\t\n", $cgi->param("annotation"),$cgi->param("file");
	}
	close $fh;
}
