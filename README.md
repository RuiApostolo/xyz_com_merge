# xyz\_com\_merge

Merges an xyz file with a .dat file, for example, with a new atom position, or the COM of a system.

## Requirements

[Python 3][python].

## Usage

The [python file](xyz_com_merge.py) uses as input two files:

* An .xyz file -- default=`system.xyz` -- for the targe system, with the normal syntax:
  * One line for the atom number `N`.
  * One line with a comment text string.
  * `N` lines, with one atom per line, with the form `atom_type x y z` separated by whitespace.
* A .dat file -- default=`com.dat` -- for the COM of the system, which should consist of nothing but the `x y z` coordinates of
  the COM, separated with spaces, one line per timestep.

Both files must have the same number of timesteps.

Optionally, two arguments controlling:

* The name of the output file -- default=`xyz_with_com.xyz`
* The atom\_type of the new atom -- default=`X`

## Example

    python3 xyz_com_merge.py --inxyz micelle.xyz --indat com.dat --out micelle_with_com.xyz --atomtype 'COM'



[python]: <https://www.python.org/downloads/> (Download Python 3)



