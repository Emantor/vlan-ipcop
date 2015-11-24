#!/usr/bin/perl
#
################################################################################
#
# IPCop VLan Configuration CGI
#   Web Interface to configure VLan Interfaces on your IPCop
#
# Copyright (C) 2006-2010 crazy_penguin
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110, USA
#
#
# Dieses Programm ist freie Software. Sie knoenen es unter den Bedingungen der GNU General Public License, wie von der Free Software Foundation veroeffentlicht, weitergeben und/oder modifizieren, entweder gemas Version 2 der Lizenz oder (nach Ihrer Option) jeder spaeteren Version.
#
# Die Veroeffentlichung dieses Programms erfolgt in der Hoffnung, dass es Ihnen von Nutzen sein wird, aber OHNE IRGENDEINE GARANTIE, sogar ohne die implizite Garantie der MARKTREIFE oder der VERWENDBARKEIT FUER EINEN BESTIMMTEN ZWECK. Details finden Sie in der GNU General Public License.
#
# Sie sollten ein Exemplar der GNU General Public License zusammen mit diesem Programm erhalten haben. Falls nicht, schreiben Sie an die Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110, USA.
#
################################################################################
#
# Revision history:
#
# 2010-01-28 created by crazy_penguin for vlan AddOn
#

# Add entry in menu
# MENUENTRY network 070 "VLan" "vlan configuration"
#
# Make sure translation exists $Lang::tr{'VLan'}

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';
require '/usr/local/lib/vlan-lib.pl';

&Header::showhttpheaders();

my %cgiparams    = ();
my $errormessage = '';
my $error        = '';
$cgiparams{'ACTION'}     = '';
$cgiparams{'USED_COUNT'} = 0;
&General::getcgihash(\%cgiparams);

my $disabled      = '';

my $errormessage  = '';
my $infomessage  = '';
my $error_vlan   = '';

my $xtiface = '/home/httpd/cgi-bin/xtiface.cgi';

sub read_conf {

  &General::readhash('/var/ipcop/ethernet/vlan', \%VLAN::vlansettings);

  @VLAN::ifs = VLAN::get_ifs(\%VLAN::vlansettings);
  @VLAN::vlans = VLAN::get_vlans(\%VLAN::vlansettings);
  @VLAN::phy_ifs = VLAN::get_phy_ifs();

  @VLAN::vlans = VLAN::uniq(@VLAN::vlans);
  @VLAN::ifs = VLAN::uniq(@VLAN::ifs);

  &General::readhash('/var/ipcop/ethernet/settings', \%VLAN::netsettings);
  @VLAN::vifs = VLAN::get_used_vifs(\%VLAN::netsettings);

  if ( -e $VLAN::xif_conf ) {
    &General::readhash($VLAN::xif_conf, \%VLAN::xifsettings);
    my @xifs = VLAN::get_used_vifs(\%VLAN::xifsettings);
    my @vifs = @VLAN::vifs;
    @VLAN::vifs =(@vifs,@xifs);
  }
  @VLAN::ppp_vlans = VLAN::get_ppp_vlans();
}

read_conf();


$cgiparams{'VLAN_ID'}     = '';
$cgiparams{'VLAN_IF'}     = '';
$cgiparams{'VLAN_DESC'}   = '';
&General::getcgihash(\%cgiparams);

unless ($cgiparams{'ACTION'}) {
  if ( ! -e $xtiface ) {
      $errormessage = $Lang::tr{'VLan no_xiface'};;
	  #$Lang::tr{'VLan error_unknown'};
  }
  
}


if ($cgiparams{'ACTION'} eq $Lang::tr{'add'}) {
  unless ($errormessage) {
    my $vlan = $cgiparams{'VLAN_ID'};
    my $int = $cgiparams{'VLAN_IF'};
    my $ret_vlan = VLAN::check_vlan_valide($vlan);
    my $ret_dup = VLAN::check_duplicate($vlan);
    if (($ret_vlan == 0 ) && ($ret_dup == 0)) {
      if (VLAN::check_interface_valide($int) == 0 ) {
        my $cfg_vlan_if = "VLAN_" .$vlan ."_IF";
        $VLAN::vlansettings{"VLAN_" .$vlan ."_IF"} = $int;
        $VLAN::vlansettings{"VLAN_" .$vlan ."_DESC"} = $cgiparams{'VLAN_DESC'};
        &General::writehash('/var/ipcop/ethernet/vlan', \%VLAN::vlansettings);
        $infomessage = $Lang::tr{'VLan vlan_added'};
		if ( $vlan == 1 ) { 
		  $infomessage = $infomessage ."<br />" .$Lang::tr{'VLan warn_vlan1'};
        }
        read_conf();
        system("/usr/local/bin/vlan_helper " .$vlan ." >/var/tmp/vlan_helper.log 2>&1");
      } else {
        $errormessage = $Lang::tr{'VLan error_if_not_exist'};
      }
    } elsif ( $ret_vlan > 0 ) {
      $errormessage = $Lang::tr{'VLan error_idtohigh'} ."<br />" .$Lang::tr{'VLan vlan_id_space'};
    } elsif ( $ret_vlan < 0 ) {
      $errormessage = $Lang::tr{'VLan error_idtolow'} ."<br />" .$Lang::tr{'VLan vlan_id_space'};
    } elsif ( $ret_dup > 0 ) {
      $errormessage = $Lang::tr{'VLan error_exist'};
    } else {
      $errormessage = $Lang::tr{'VLan error_unknown'};
    }
    &General::log("$Lang::tr{'VLan vlan_added'}: $cgiparams{'VLAN_ID'} on $cgiparams{'VLAN_IF'}");
    undef %cgiparams;
    $cgiparams{'ACTION'} = '';
  }
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'remove'}) {
  my $vlan = $cgiparams{'VLAN_ID'};
  &General::readhash('/var/ipcop/ethernet/settings', \%VLAN::netsettings);
  @VLAN::vifs = VLAN::get_used_vifs(\%VLAN::netsettings);
  my $ret_dup = VLAN::check_duplicate($vlan);
  my $vif = $VLAN::vlansettings{"VLAN_" .$vlan ."_IF"} ."." .$vlan;
  my $ret_use = VLAN::check_used($vif);
  if (($ret_use == 0 ) && ($ret_dup == 1)) {
    my $cfg_vlan = "VLAN_" .$vlan ."_IF";
    delete($VLAN::vlansettings{"VLAN_" .$vlan ."_IF"});
	delete($VLAN::vlansettings{"VLAN_" .$vlan ."_DESC"});
    &General::writehash('/var/ipcop/ethernet/vlan', \%VLAN::vlansettings);
    system("/usr/local/bin/vlan_helper " .$vlan ." >/var/tmp/vlan_helper.log 2>&1");
    $infomessage = $Lang::tr{'VLan vlan_removed'};
    read_conf();
  } elsif ( $ret_dup == 0 ) {
    $errormessage = $Lang::tr{'VLan error_not_exist'};
  } elsif ( $ret_use > 0 ) {
    $errormessage = $Lang::tr{'VLan error_inuse'};
  } else {
    $errormessage = $Lang::tr{'VLan error_unknown'};
  }
  &General::log("$Lang::tr{'VLan vlan_removed'}: $cgiparams{'VLAN_ID'} from $cgiparams{'VLAN_IF'}");
  undef %cgiparams;
  $cgiparams{'ACTION'} = '';
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'update'}) {
  my $vlan = $cgiparams{'VLAN_ID'};
  $VLAN::vlansettings{"VLAN_" .$vlan ."_DESC"} = $cgiparams{'VLAN_DESC'};
  &General::writehash('/var/ipcop/ethernet/vlan', \%VLAN::vlansettings);
  $infomessage = $Lang::tr{'VLan vlan_updated'};
  &General::log("$Lang::tr{'VLan vlan_updated'}: $cgiparams{'VLAN_ID'} with $cgiparams{'VLAN_DESC'}");
  undef %cgiparams;
  $cgiparams{'ACTION'} = '';
}


if ($cgiparams{'ACTION'} eq $Lang::tr{'reset'}) {
  undef %cgiparams;
  $cgiparams{'ACTION'} = '';
}


&Header::openpage($Lang::tr{'VLan configuration'}, 1, '');
&Header::openbigbox('100%', 'left', '');

if ($errormessage) {
  &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
  print "<font class='base'>$errormessage&nbsp;</font>\n";
  &Header::closebox();
}

if ($infomessage) {
  &Header::openbox('100%', 'left', $Lang::tr{'warning messages'}, 'warning');
  print "<b>$Lang::tr{'note'}:</b><br />$infomessage\n";
  &Header::closebox();
}


my %selected = ();
foreach my $if (@VLAN::phy_ifs) {
  $selected{'INTERFACE'}{'$if'} = '';
}
my $used_if = $VLAN::vlansettings{"VLAN_" .$cgiparams{'VLAN_ID'} ."_IF"};
$selected{'INTERFACE'}{'$used_if'} = "selected='selected'";

my $cfg_vlan_desc = '';
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
  $cfg_vlan_desc = $VLAN::vlansettings{"VLAN_" .$cgiparams{'VLAN_ID'} ."_DESC"};
  $disabled = "disabled='disabled'";
}


&Header::openbox('100%', 'left', "$Lang::tr{'VLan configuration'}:", $error_vlan);
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

if (($VLAN::vlan_count == 4) && ( -e $xtiface ) ) {
  print "<strong>$Lang::tr{'note'}</strong>:&nbsp;$Lang::tr{'VLan vlan_eq_4'}<br />";
} elsif ( ($VLAN::vlan_count > 4 ) && ( -e $xtiface ) ) { 
  print "<strong>$Lang::tr{'note'}</strong>:&nbsp;$Lang::tr{'VLan vlan_gt_4'}<br />";
}

print <<END
<table width='100%'>
<tr>
  <td>$Lang::tr{'VLan vlan_id'}:</td><td>
    <input type='text' name='VLAN_ID' value='$cgiparams{'VLAN_ID'}' size='4' maxlength='4' $disabled />
  </td>
  <td>$Lang::tr{'VLan interface'}:</td><td>
        <select name='VLAN_IF' $disabled >
END
    ;
foreach my $if (@VLAN::phy_ifs) {
  print "<option value='$if' $selected{'INTERFACE'}{'$used_if'}>" .$if ."</option>";
}
print <<END
        </select>

  </td>
</tr>
<tr>
  <td>$Lang::tr{'VLan description'} <img src='/blob.gif' alt='*' align='top' />:</td><td colspan='3'>
    <input type='text' name='VLAN_DESC' value='$cfg_vlan_desc' size='40' maxlength='40'/>
  </td>

</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='comment2buttons'>
        <strong>$Lang::tr{'note'}</strong>:&nbsp;$Lang::tr{'VLan vlan_id_space'}
    </td>
    <td colspan='3'>&nbsp;</td>
</tr>
END
   ;
if ( @VLAN::ppp_vlans > 0 ) {
  print "<tr>";
  print "    <td class='comment2buttons'>";
  print "        <strong>$Lang::tr{'note'}</strong>:&nbsp;$Lang::tr{'VLan ppp_vlans'}<strong>";
  foreach my $tags ( @VLAN::ppp_vlans) { 
    print "&nbsp;$tags";
  }
  print "</strong>";
  print "    </td>";
  print "    <td colspan='3'>&nbsp;</td>";
  print "</tr>";
}
print <<END
<tr>
    <td class='comment2buttons'>
        <img src='/blob.gif' alt='*' align='top' />&nbsp;$Lang::tr{'this field may be blank'}
    </td>
END
   ;

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
  print "<td class='button2buttons'><input type='submit' name='ACTION' value='$Lang::tr{'update'}' />\n";
  print "<input type='hidden' name='OLD_VLAN_IF' value='$cgiparams{'VLAN_IF'}' /></td>\n";
  print "<input type='hidden' name='VLAN_ID' value='$cgiparams{'VLAN_ID'}' /></td>\n";
} else {
  print "<td class='button2buttons'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td>\n";
}
print <<END;
    <td class='button2buttons'>
        <input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />
    </td>
</tr>
</table>


END
    ;
print "</form>\n";

&Header::closebox();


&Header::openbox('100%', 'left', "$Lang::tr{'VLan configuration'}:", $error_vlan);
print <<END
<div align='center'>
<table width='100%' align='center'>
<tr align="center">
    <td width='10%'><strong>$Lang::tr{'VLan vlan_id'}</strong></td>
    <td width='10%'><strong>$Lang::tr{'VLan interface'}</strong></td>
    <td width='30%'><strong>$Lang::tr{'VLan description'}</strong></td>
    <td width='5%'>&nbsp;</td>
    <td width='5%'>&nbsp;</td>
    <td width='40%'>&nbsp;</td>
</tr>

END
    ;
my $id = 0;

foreach my $vlan (sort @VLAN::vlans) {
  if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'VLAN_ID'} eq $vlan) {
    print "<tr class='selectcolour'>\n";
  } else {
    print "<tr class='table".int(($id % 2) + 1)."colour'>";
  }
  print <<END;
      <td align='center'>$vlan</td>
      <td align='center'>$VLAN::vlansettings{"VLAN_" .$vlan ."_IF"}</td>
      <td align='center'>$VLAN::vlansettings{"VLAN_" .$vlan ."_DESC"}</td>
END
if ( VLAN::check_used($VLAN::vlansettings{"VLAN_" .$vlan ."_IF"} ."." .$vlan) == 0 ) {
  print <<END;
      <td align='center'>
      <form method='post' name='frm$vlan' action='$ENV{'SCRIPT_NAME'}'>
        <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
        <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}'/>
        <input type='hidden' name='VLAN_ID' value='$vlan' />
      </form>
      </td>
END
print <<END;
    <td align='center'>
    <form method='post' name='frmb$vlan' action='$ENV{'SCRIPT_NAME'}'>
        <input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
        <input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}'/>
        <input type='hidden' name='VLAN_ID' value='$vlan' />
    </form>
    </td>
END
} else {
  print <<END;
      <td align='center'>&nbsp;</td>
      <td align='center'>&nbsp;</td>
END
}
  print <<END;
  </tr>
END
 $id++;
}

print <<END
</table>
</div>

<br />
<hr />
<br />
END
;

my @vifconfig = `ifconfig -a | grep -e  '^[a-z]*-[0-9]\\.' -A 7`;
print join("<br />",@vifconfig),"\n";

print <<END
<table width='100%'>
<tr>
    <td class='onlinehelp'>
    </td>
</tr>
</table>
END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();


