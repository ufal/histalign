use XML::LibXML;
use JSON;
use Encode qw(decode);

$\ = "\n"; $, = "\t";
$input = shift;

$/ = undef;
open FILE, $input;
# binmode ( FILE, ":utf8");
$raw = <FILE>;
close FILE;

$data = decode_json($raw);

# print JSON->new->utf8->pretty->encode($data);

$parser = XML::LibXML->new(); 
$xml1 = $parser->load_xml(location => $data->{'version1'});
$xml2 = $parser->load_xml(location => $data->{'version2'});

foreach $item ( @{$data->{'sentences'}} ) {
	$id1 = $item->{'id1'};
	$id2 = $item->{'id2'};
	
	print "Match:", $id1, $id2;
	@tuids = ();
	foreach $sid ( split(",", $id1) ) {
		foreach $sent ( $xml1->findnodes("//s[\@id='$sid']") ) { 
			$tuid = $sent->getAttribute('tuid');
			if ( $tuid ) { push(@tuids, $tuid); };
		};
	};
	$alignid = join("|", @tuids);
	print "Source: $alignid";

	foreach $sid ( split(",", $id2) ) {
		foreach $sent ( $xml2->findnodes("//s[\@id='$sid']") ) { 
			$tuid = $sent->getAttribute('tuid');
			if ( !$tuid || $force ) { 
				 $sent->setAttribute('tuid', $alignid);
				print "Set:", $sid, $alignid;
			};
		};
	};
	
};

$outfile = $data->{'version2'}."";
open FILE, ">$outfile";
print FILE $xml2->toString;
close FILE;