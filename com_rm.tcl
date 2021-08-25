###############################################################################
# This script creates an xyz file for a micelle and its COM                   #
# Intended to be used with xyz_com_merge.py                                   #
# Created by Rui Apóstolo                                                     #
# Version 1.0 August 2021                                                     #
###############################################################################
#                             EDITABLE PARAMETERS                             #
###############################################################################
# set micelle atom types
set micelle_names "not type 8 9 10"
# load trajectory file
mol new dump.trimmed.lammpstrj type lammpstrj waitfor all autobonds off
# set start
set ts_start 0
# end of last range (relative to dump file start, first timestep is always 0)
set ts_stop [expr [molinfo top get numframes] - 1]
# set skip (== 1 outputs every timestep)
set ts_skip 1
# COM coordinate file name
set com_file "com.dat"

###############################################################################
#                         END OF EDITABLE PARAMETERS                          #
###############################################################################
package require pbctools
package require topotools

puts " "
puts " "
puts "Loading complete, writing COM coordinates file"
puts " "

# TODO: loop starts here

# set micelle atom selection
set micelle [atomselect top $micelle_names]
# remove periodic imates
pbc wrap -sel $micelle_names -first $ts_start -last $ts_stop
# open output file
set fout1 [open $com_file w+]
# FOR loop from ts_start to ts_stop with step ts_skip
for {set i $ts_start} {$i <= $ts_stop} {incr i $ts_skip} {
  # set timestep
  $micelle frame $i
  $micelle update
  # Calculate COM from micelle
  # micelle_com is an array size 3
  set micelle_com [measure center $micelle weight mass]
  puts $fout1 "${micelle_com}"
}
close $fout1

puts " "
puts "Writing micelle XYZ file"
puts " "

animate write xyz "micelle.xyz" beg $ts_start end $ts_stop skip $ts_skip waitfor all sel $micelle 

exit
