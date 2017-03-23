#!/usr/bin/env perl -w

use strict;

my @files = `ls sgb`;

sub main() {
    foreach my $f (@files) {
	my $ctx = 0; # context: vertices=0, edges=1 
	my $V = 0; # number of vertices
	my $E = 0; # number of edges
	my %vertices; # label of vertices
	my %v_index; # index of vertices
	my %e_weight; # hash of edges weights
	my %freq; # frequency of vertices

	chomp $f;

	# pajek file name
	my ($base, $ext) = split(/\./, $f);
	my $net = $base.".net";
	my $freq_f = $base.".freq";
	
	open(DAT, "sgb/$f");
	while (<DAT>) {
	    if ($_ =~ /^\*/) {
		next;
	    }

	    if ($_ =~ /^\n/) {
		$ctx = 1;
		next;
	    }
	    
	    # Vertices
	    if ($ctx == 0) {
		my ($first, $rest) = split(/ /, $_, 2);

		$rest =~ s/\n//;
		$vertices{$first} = $rest;
		$V++;
		$v_index{$first} = $V;
	    }

	    # Edges
	    if ($ctx == 1) {
		my ($chapter, $rest) = split(/:/, $_, 2);

		# verify empty chapters
		$rest = "" unless defined $rest;
		if ($rest eq "") {
		    next;
		}

		chomp($rest);
		
		my @edges = split(/;/, $rest);

		foreach my $es (@edges) {
		    my @verts = split(/,/, $es);

		    # Calculate the frequency
		    foreach my $v (@verts) {
			if (exists($freq{$v})) {
			    $freq{$v}++;
			    
			} else {
			    $freq{$v} = 1;
			}
		    } 
		    
		    # Generate the edges
		    for	(my $i=0; $i < $#verts; $i++) {
			for (my $j=$i+1; $j <= $#verts; $j++) {
			    my $e = $v_index{$verts[$i]}." ".$v_index{$verts[$j]};
			    
			    if (exists($e_weight{$e})) {
				$e_weight{$e}++;
			    } else {
				$E++;
				$e_weight{$e} = 1;
			    }
			}
		    }
		} # foreach my $es
		
	    } 
	    
	}
	close(DAT);
	print "INFO: Generating $net\n";
	open(NET, ">$net");
	print NET "*Vertices $V\n";
	for my $v (sort keys %vertices) {
	    print NET $v_index{$v}." \"".$v."\"\n";
	}
	print NET "*Edges\n";
	for my $e (sort keys %e_weight) {
	    print NET $e." ".$e_weight{$e}."\n";
	}
	close(NET);

	print "INFO: Generating $freq_f\n";
	open(FREQ, ">$freq_f");
	for my $v (sort {$freq{$b} <=> $freq{$a}} keys %freq) {
	    print FREQ "\"".$v."\";".$freq{$v}."\n";
	}
	#last;
    }
}

main();
