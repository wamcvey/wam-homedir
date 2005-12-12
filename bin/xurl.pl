#!/usr/bin/perl -w -s
# extract urls
# "cause qxurl from perlfaq9 just wasn't good enough"
# Mostly stolen from manpage for HTML::TokeParser
#
# William McVey
# July 27, 2001

require 5.002;
use HTML::TokeParser;

$p = HTML::TokeParser->new(shift||*STDIN);

$v=0;
while (my $token = $p->get_tag("a")) {
	my $url = $token->[1]{href} || "-";
	my $text = $p->get_trimmed_text("/a");
	if ($v) { 
		print "$url\t$text\n"; 
	} else {
		print "$url\n";
	}
} 
