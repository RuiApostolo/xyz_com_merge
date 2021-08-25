#!/usr/bin/python3
"""
xyz_com_merge.py
Created by Rui Apóstolo
Version 1.0 August 2021
This script merges an xyz file with a com.dat file with coordinates for a COM
Initially intended to be used with a VMD tcl/tk script that calculates
the COM for a micelle and writes the COM coordinates as a com.dat file
with the structure:
    {x} {y} {z}
    number of lines: number of timesteps
Result is a merged xyz file.
"""
from mmap import mmap
from copy import deepcopy

###############################################################################
#                             EDITABLE PARAMETERS                             #
###############################################################################
xyzfile = 'micelle.xyz'
comfile = 'com.dat'
outfile = 'micelle_with_com.xyz'

###############################################################################
#                         END OF EDITABLE PARAMETERS                          #
###############################################################################


class XYZ:
    """
    XYZ file-style class.
    """

    def __init__(self, filename):
        """
        Init function for XYZ class.

        Args:
            filename: file from where to read the XYZ structure from.
        """
        self.filename = filename
        self.numsteps = self.tsCount(filename)
        self.frames = self.read(filename)
        self.size = self.molSize(self.frames)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.frames[self.index]
        except IndexError as err:
            raise StopIteration from err
        self.index += 1
        return item

    def __str__(self):
        return f"File: {self.filename}, steps: {self.numsteps}, molSize: {self.size}" #noqa

    def tsCount(self, filename: str) -> int:
        """
        Counts the number of timesteps in the XYZ file,
        accounts for molecule size.

        Args:
            filename: The name of the file to count the lines of.

        Returns:
            The number of timesteps in the XYZ file.

        Raises:
            TypeError: If the function calculates a number of timesteps that is
                not an integer.
        """
        with open(filename) as f:
            size = f.readline()
        steps = fileLen(filename) / (int(size) + 2)
        if steps.is_integer():
            return int(steps)
        else:
            raise TypeError('XYZ timestep calculation did not return an integer.')  # noqa

    def read(self, filename: str) -> dict:
        """
        Reads the XYZ file and yields one timestep at a time.

        Args:
            filename: The name of the file to read timesteps from.

        Returns:
            The coordinates from the XYZ file, one timestep at a time.
        """
        with open(filename, 'r') as f:
            index = 0
            frames = {}
            while True:
                frame = {}
                molsize = f.readline().strip()
                if not molsize:
                    break
                molsize = int(molsize)
                frame['molsize'] = molsize
                comment = f.readline()
                if not comment:
                    raise StopIteration('Out of lines in XYZ file when trying to read comment.')  # noqa
                    break
                frame['comment'] = comment
                frame['atoms'] = []
                for i in range(0, molsize):
                    line = f.readline().strip().split()
                    if not line:
                        raise StopIteration('Out of lines in XYZ file when trying to read frames.')  # noqa
                        break
                    new_atom = ATOM(
                        str(line[0]),
                        float(line[1]),
                        float(line[2]),
                        float(line[3])
                        )
                    frame['atoms'].append(new_atom)
                frames[index] = frame
                index += 1
            return frames

    def molSize(self, frames: dict) -> int:
        """
        Check whether the size of the molecule is consistent.

        Args:
            frames: The frames read from the XYZ file.

        Returns:
            molSize for every timestep has the same size.
            Returns 0 if molSize differs.
        """
        size_list = []
        for frame in frames:
            size_list.append(frames[frame]['molsize'])
        size_set = set(size_list)
        if len(size_set) == 1 and size_list[0] != 0:
            mol_size = size_list[0]
            return mol_size
        else:
            return 0

    def merge(self, com: object) -> object:
        """
        Function that merges the XYZ and COM objects into a new XYZ object.

        Args:
            com: The COM object.

        Returns:
            A new XYZ obect
        """
        # Check that numsteps is equal in both objects
        try:
            timestepsCOM = com.numsteps
            timestepsXYZ = self.numsteps
            isEqual(timestepsCOM, timestepsXYZ)

        except ValueError as err:
            raise ValueError from err

        new_xyz = deepcopy(self)
        new_xyz.size += 1
        for frame in self.frames:
            self.frames[frame]['atoms'].append(com.frames[frame])

        return new_xyz

    def save(self, outfile):
        with open(outfile, 'w') as f:
            for frame in self.frames:
                f.write(f"{self.size}\n")
                f.write("Created by xyz_com_merge.py\n")
                for atom in self.frames[frame]['atoms']:
                    f.write(f"{atom}\n")


class COM(list):
    """
    Centre of mass class.
    """

    def __init__(self, filename):
        """
        Init function for COM file class.

        Args:
            filename: file from where to read the XYZ structure from.
        """
        self.filename = filename
        self.numsteps = self.tsCount(filename)
        self.frames = self.read(filename)
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.frames[self.index]
        except IndexError as err:
            raise StopIteration from err
        self.idx += 1
        return item

    def __str__(self):
        return f"File: {self.filename}, steps: {self.numsteps}"

    def tsCount(self, filename: str) -> int:
        """
        Counts the number of 'timesteps' in the .dat file.

        Args:
            filename: The name of the file to count the timesteps of.

        Returns:
            The number of timesteps in the .dat file.
        """
        steps = fileLen(filename)
        return steps

    def read(self, filename: str) -> dict:
        """
        Reads the COM file and yields one timestep at a time.

        Args:
            filename: The name of the file to read timesteps from.

        Returns:
            A dictionary of atom objects with the form:
                { timestep: atom }
        """
        with open(filename, 'r') as f:
            indx = 0
            coords = {}
            while True:
                line = f.readline().split()
                if not line:
                    break
                new_atom = ATOM("X", line[0], line[1], line[2])
                coords[indx] = new_atom
                indx += 1
            return coords


class ATOM:
    """
    ATOM class.
    """

    def __init__(self, atom_type: str, x: float, y: float, z: float):
        """
        Init function for atom class.

        Args:
            atom_type: Type of atom.
            x: X coordinate.
            y: Y coordinate.
            z: Z coordinate.
        """
        self.atom_type = atom_type
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return(f"{self.atom_type} {self.x} {self.y} {self.z}")

    def __repr(self):
        return self.__str__


def fileLen(filename: str) -> int:
    """
    Counts the number of lines a file.
    Source: https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python #noqa

    Args:
        filename: The name of the file to count the lines of.

    Returns:
        The number of lines in the file.
    """
    f = open(filename, "r+")
    buf = mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines


def isEqual(a: int, b: int):
    """
    Check whether two variables are equal.

    Args:
        a: First variable to check.
        b: Second variable to check.

    Returns:
        True if variables are equal. False otherwise.

    Raises:
        ValueError: If the variables are different if
    """
    if a != b:
        raise ValueError('XYZ and COM files have different timestep numbers.')
        return False
    return True


def main():
    """
    Main function. Handles exceptions.
    """
    try:
        print("Loading files.")
        micelle = XYZ(xyzfile)
        print(f"Micelle -- {micelle}")
        com = COM(comfile)
        print(f"COM -- {com}")
        print("Merging files.")
        micelle_with_com = micelle.merge(com)
        print(f"Saving file {outfile}.")
        micelle_with_com.save(outfile)
        return

    except TypeError as err:
        raise TypeError from err
    except ValueError as err:
        raise ValueError from err
    except StopIteration as err:
        raise StopIteration from err
    return


if __name__ == '__main__':
    main()
