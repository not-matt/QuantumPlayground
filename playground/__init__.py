import requests
import argparse
import os
import sys
import logging
import xml.etree.ElementTree as ET
import numpy as np
import copy

#from functools import lru_cache

from playground.utils import elements
from playground.basis_set import get_basis_set
from playground.plot import plot_implicit

class Molecule(object):
    def __init__(self, atoms: dict, bonds: dict):
        """
        atoms - dict of Atom instances by id
        bonds - dict of bonds by bondRef eg. {"id1 id2": bondOrder}
        """
        self._atoms = atoms
        self._bonds = bonds
        self.n_electrons = sum(atom.atomic_number for atom in self)

    def apply_basis_set(self, basis_set):
        for atom in self:
            atom.orbitals = copy.deepcopy(basis_set[atom.symbol])
            for orbital in atom.orbitals:
                orbital.centre = atom.centre

    def __repr__(self):
        return "\n".join(str(atom) for atom in self)

    def __iter__(self):
        return iter(self._atoms.values())

    def __call__(self, x, y, z):
        return sum(ao(x, y, z) for ao in self.orbitals)

    @property
    def orbitals(self):
        mos = []
        for atom in self:
            mos.extend(atom.orbitals)
        return mos
    
    @property
    def coordinates(self):
        return np.array([np.array(atom.centre) for atom in self])
    
    @property
    def atom_types(self):
        return list(atom.symbol for atom in self)

    @property
    def bonds(self):
        atom_ids = list(self._atoms.keys())
        bonds = []
        for bond in self._bonds:
            id1, id2 = bond.split()
            bonds.append((atom_ids.index(id1), atom_ids.index(id2)))
        return bonds

class Atom(object):
    def __init__(self, symbol: str, centre: tuple):
        """
        symbol - str - atomic symbol
        centre - tuple, (float * 3) - x,y,z coordinates
        """
        self.symbol = symbol
        self.centre = centre
        self.atomic_number, self.name = elements[self.symbol]
        self.orbitals = None

    def __repr__(self):
        orbitals = '\n        '.join(str(ao) for ao in self.orbitals)
        return f"{self.name}:\n    position {self.centre}\n    orbitals\n        {orbitals}"

# def parse_xyz(file: str):
#     with open(file) as file_handle:
#         n_atoms = file_handle.readline().strip()
#         title = file_handle.readline().strip()
#         atoms = []
#         for line in file_handle:
#             symbol, x, y, z = line.strip().split()
#             x = float(x)
#             y = float(y)
#             z = float(z)
#             atom = Atom(symbol, (x, y, z))
#             atoms.append(atom)
#         return atoms

def parse_cml(file: str):
    root = ET.parse(file).getroot()
    atomArray = root.find("atomArray")
    bondArray = root.find("bondArray")

    atoms = {}
    for item in atomArray:
        atomID = item.attrib["id"]
        atom = Atom(item.attrib["elementType"], ( # convert angstrom to au
                        float(item.attrib["x3"]) * 1.8897261339213,
                        float(item.attrib["y3"]) * 1.8897261339213,
                        float(item.attrib["z3"]) * 1.8897261339213
                    ))
        atoms[atomID] = atom

    bonds = {}
    for item in bondArray:
        bondID = item.attrib["atomRefs2"]
        bonds[bondID] = item.attrib["order"]

    return atoms, bonds

def setup_logging(loglevel):
    global _LOGGER
    _LOGGER = logging.getLogger(__name__)

    console_loglevel = loglevel or logging.WARNING
    console_logformat = "[%(levelname)-8s] %(name)-30s : %(message)s"

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_loglevel)  # set loglevel
    console_formatter = logging.Formatter(
        console_logformat
    )  # a simple console format
    console_handler.setFormatter(
        console_formatter
    )  # tell the console_handler to use this format

    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.addHandler(console_handler)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieves basis sets from the Basis Set Exchange - https://www.basissetexchange.org/"
    )

    parser.add_argument(
        "input_file",
        help="Input XYZ file defining atom coordinates",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="verbose logs to console",
        action="store_const",
        const=logging.INFO,
    )

    parser.add_argument(
        "-b",
        "--basis_set",
        dest="basis_set",
        default="6-31G*",
        help="Basis Set to use, default 6-31G*. For full options, see https://www.basissetexchange.org/",
    )

    return parser.parse_args()

class Playground(object):
    def __init__(self, loglevel=logging.INFO):
        setup_logging(loglevel)

        # demo plot
        # plot_implicit(next(iter(molecule)).orbitals[1], 0.05, [-10,10], 0, 90) #Pz orbital on Oxygen.

    def open(self, input_file: str, basis_set: str ="6-31G*"):
        # Read and parse the input cml file
        if not os.path.exists(input_file):
            _LOGGER.error(f"Cannot find input file '{input_file}'")
            return 1
        # atoms = parse_xyz(input_file)
        atoms, bonds = parse_cml(input_file)
        molecule = Molecule(atoms, bonds)
        _LOGGER.info("Parsed CML input file")

        # Collect, parse, and generate the basis set for the atoms 
        try:
            _LOGGER.info("Retrieving basis set...")
            basis_set = get_basis_set(basis_set, tuple(atom.atomic_number for atom in molecule))
        except Exception as e:
            _LOGGER.error(e)
            _LOGGER.info(f"You're likely seeing this error because an atom from '{input_file}' is not defined in the basis set '{basis_set}'. For more details see https://www.basissetexchange.org/")
            return

        # Apply the basis set to the atoms
        molecule.apply_basis_set(basis_set)
        _LOGGER.info("Applied basis set to molecule")
        for line in str(molecule).split("\n"):
            _LOGGER.info(line)

        return molecule


# def main():
#     args = parse_args()
#     setup_logging(args.loglevel)

#     # Read and parse the input.xyz file
#     input_file = args.input_file
#     if not os.path.exists(input_file):
#         _LOGGER.error(f"Cannot find input file '{input_file}'")
#         return 1
#     # atoms = parse_xyz(input_file)
#     atoms, bonds = parse_cml(input_file)
#     molecule = Molecule(atoms, bonds)
#     _LOGGER.info("Parsed CML input file")

#     # Collect, parse, and generate the basis set for the atoms 
#     try:
#         _LOGGER.info("Retrieving basis set...")
#         basis_set = get_basis_set(args.basis_set, tuple(atom.atomic_number for atom in molecule))
#     except Exception as e:
#         _LOGGER.error(e)
#         _LOGGER.info(f"You're likely seeing this error because an atom from '{input_file}' is not defined in the basis set '{args.basis_set}'. For more details see https://www.basissetexchange.org/")
#         return

#     # Apply the basis set to the atoms
#     molecule.apply_basis_set(basis_set)
#     _LOGGER.info("Applied basis set to molecule")
#     for line in str(molecule).split("\n"):
#         _LOGGER.info(line)

#     # demo plot
#     # plot_implicit(next(iter(molecule)).orbitals[1], 0.05, [-10,10], 0, 90) #Pz orbital on Oxygen.
#     coordinates = np.array([np.array(atom.centre) for atom in molecule])
#     atom_types = [atom.symbol for atom in molecule]
#     mv = MolecularViewer(coordinates, topology={'atom_types': atom_types})
#     mv.lines()
#     mv

# if __name__ == "__main__":
#     sys.exit(main())
