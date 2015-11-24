#!/usr/bin/perl


package VLAN;

require '/usr/lib/ipcop/general-functions.pl';

my %vlansettings;
my %netsettings;
my %xifsettings;
my %pppsettings;
my @vlans;
my @ifs;
my @phy_ifs;
my @vifs;
my @ppp_vlans;
my $vlan_count;

$vlan_conf = '/var/ipcop/ethernet/vlan';
$eth_conf  = '/var/ipcop/ethernet/settings';
$ppp_conf  = '/var/ipcop/ppp/settings';
$xif_conf  = '/var/ipcop/addons/xtiface/xtiface.conf';

1;



#make entries in an array uniq
sub uniq {
    my %seen = ();
    my @r = ();
    foreach my $a (@_) {
        unless ($seen{$a}) {
            push @r, $a;
            $seen{$a} = 1;
        }
    }
    return @r;
}

sub get_ifs {
  # read used interfaces from hash
  my @r = ();
  my %if_hash = %{(shift)};
  foreach my $var (keys %if_hash) {
    if ($var =~ m/^VLAN_[0-9]{1,4}_IF/) {
      #print $var ." - " .$if_hash{"$var"} ."\n";
      push(@r,$if_hash{"$var"});
    }
  }
  return @r;
}

sub get_vifs {
  # read used interfaces from hash
  my @r = ();
  my %if_hash = %{(shift)};
  foreach my $var (keys %if_hash) {
    if ($var =~ m/^VLAN_[0-9]{1,4}_IF/) {
      $var =~ m/[0-9]{1,4}/;
      my $vif = $if_hash{"$var"} ."." .$&;
      #print $var ." - " .$vif ."\n";
      push(@r,$vif);
    }
  }
  return @r;
}

sub get_vlans {
  # read used vlans from hash
  my @r = ();
  my %vl_hash = %{(shift)};
  foreach my $var (keys %vl_hash) {
    if ($var =~ m/^VLAN_[0-9]{1,4}/) {
      $var =~ m/[0-9]{1,4}/;
      push(@r,$&);
      #print $var ." - " .$vl_hash{"$var"} ." - " .$& ."\n";
    }
  }
  #$VLAN::vlan_count = VLAN::uniq(@r);
  return @r;
}

sub get_phy_ifs {
  my @ifaces_list_all = `cat /proc/net/dev | grep -e '.*:'`;
  my @phy_ifs = ();
  foreach my $line ( sort @ifaces_list_all ) {
    chomp($line);               # remove newline
    #print $line;
    #print index($line, "lo") ."\n";
    if ( index($line, "lo") == -1 ) {
      $line =~ /\s*([a-z]*\-\d+)\s*/;
      push(@phy_ifs,$1);
    }
  }
  return uniq(@phy_ifs);
}

sub get_used_vifs {
  # read used interfaces from hash
  my @r = ();
  my %if_hash = %{(shift)};
  foreach my $var (keys %if_hash) {
    if ($var =~ m/_[0-9]_DEV$/) {
      if ($if_hash{"$var"} =~ m/\.[0-9]{1,4}$/ ) {
      #print $var ." - " .$if_hash{"$var"} ."\n";
      push(@r,$if_hash{"$var"});
      }
    }
  }
  return @r;
}

sub trim{
   my $string = shift;
   $string =~ s/^\s+|\s+$//g;
   return $string;
}

sub check_duplicate {
  my $r;
  my $id = @_[0];
  $id = trim($id);
  foreach my $vlan ( sort @VLAN::vlans) { 
    if ( $vlan eq $id ) {
      return 1;
    }
  }
  return 0;
}

sub check_interface_valide() {
  my $ret = 1;
  my $int = @_[0];
  $int = trim($int);
  foreach my $if ( sort @VLAN::phy_ifs ) {
    if ( $int eq $if ) {
      return 0;
    } else {
    }
  }
  return $ret;
}

sub check_vlan_valide() {
  my $r;
  my $id = @_[0];
  if ( $id > 4094 ) {
    $r = 1;
  } elsif ( $id < 1 ) {
    $r = -1;
  } else { 
    $r = 0;
  }
  return $r;
}

sub check_used() {
  my $r = 0;
  my $vint = @_[0];
  $int = trim($int);
  foreach my $if ( sort @VLAN::vifs ) {
    if ( $vint eq $if ) {
      #print "Inuser - VINT: ".$vint ."  IF: " .$if ."\n";
      return 1;
    } else {
      #print "Not inuser - VINT: ".$vint ."  IF: " .$if ."\n";

    }
  }
  
  return $r;
}

sub get_ppp_vlans() {
  &General::readhash($VLAN::ppp_conf, \%VLAN::pppsettings);
  my @r = ();
  foreach my $var (keys %VLAN::pppsettings) {
    if ($var =~ m/^VDSL_TAG/) {
      my $tag = $VLAN::pppsettings{"$var"};
      push(@r,$tag);
    }
  }
  return @r;
  
}

# EOF
