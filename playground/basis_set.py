import requests
import logging
import numpy as np

from playground.utils import elements, angular_quanta

_LOGGER = logging.getLogger(__name__)

class AO(object):
    """
    atomic orbital
    """
    def __init__(self, 
                 orbital_type: str, 
                 contract_num: int, 
                 exponents: list,
                 coeffs: list,
                 centre: tuple = (0, 0, 0)):
        """
        orbital_type - eg. s, px, dx2
        contract_num - G contraction factor
        exponents - G exponents list
        coeffs - G coefficients list
        centre - tuple, (float * 3) - x,y,z coordinates
        """
        self.orbital_type = orbital_type
        self.contract_num = contract_num
        self.exponents = exponents
        self.coeffs = coeffs
        self.centre = centre
        self.angular = angular_quanta[orbital_type]

    def __repr__(self):
        return f"<Atomic Orbital, type {self.orbital_type}>"

    def __call__(self, x, y, z):
        res = 0
        x0, y0, z0 = self.centre
        l, m, n = self.angular

        for i in range(len(self.coeffs)):
            exponent = self.exponents[i]
            gprimitivex = Gprimitive(l, x0, exponent)
            gprimitivey = Gprimitive(m, y0, exponent)
            gprimitivez = Gprimitive(n, z0, exponent)
            res += self.coeffs[i]*gprimitivex(x)*gprimitivey(y)*gprimitivez(z)
        return res

class Gprimitive: #gaussian primitive class for only one variable. The total will be product of gprimitive(x)*gprimitive(y)*gprimitive(z)
    def __init__(self, angular, centre, exponent):
        self.angular = angular
        self.centre = centre
        self.exponent = exponent
    
    def __call__(self, x):
        return (x-self.centre)**self.angular * np.exp(-self.exponent*(x-self.centre)**2)

def parse_basis_lines(basis_lines: str):
    """
    Handles creating the atomic orbitals for one atom of the basis set.
    basis_lines is a list of each line of the basis set information in "gaussian94" format
    """
    orbitals = []
    lines = iter(basis_lines)
    atom_symbol, _ = next(lines).split()
    while True:
        try:
            orbital_type, contract_num, _ = next(lines).split()
            contract_num = int(contract_num)

            if orbital_type == "F":
                msg = "F orbitals are not yet supported. Please choose a simpler basis set"
                raise ValueError(msg)

            # SP orbitals have an extra coefficient parameter for the p orbitals that need to be handled separately
            if orbital_type == "SP":
                exponents = []
                coeffs = []
                coeffps = []
                for i in range(contract_num):
                    exponent, coeff, coeffp = next(lines).replace("D", "e").split()
                    exponents.append(float(exponent))
                    coeffs.append(float(coeff))
                    coeffps.append(float(coeffp))
            else:
                exponents = []
                coeffs = []
                for i in range(contract_num):
                    exponent, coeff = next(lines).replace("D", "e").split()
                    exponents.append(float(exponent))
                    coeffs.append(float(coeff))

            assert len(exponents) == contract_num
            assert len(coeffs) == contract_num

            if orbital_type == "S":
                s = AO("S", contract_num, exponents, coeffs)
                orbitals.append(s)
            elif orbital_type == "P":
                for angular in ["Px", "Py", "Pz"]:
                    ao = AO(angular, contract_num, exponents, coeffs)
                    orbitals.append(ao)
            elif orbital_type == "D":
                for angular in ["Dx2", "Dy2", "Dz2", "Dxy", "Dyz", "Dzx"]:
                    ao = AO(angular, contract_num, exponents, coeffs)
                    orbitals.append(ao)
            elif orbital_type == "SP":
                s = AO("S", contract_num, exponents, coeffs)
                orbitals.append(s)
                for angular in ["Px", "Py", "Pz"]:
                    ao = AO(angular, contract_num, exponents, coeffps)
                    orbitals.append(ao)
        except StopIteration:
            break
    return atom_symbol, orbitals

def get_basis_set(basis_set: str, atomic_nos: tuple):
    """
    Performs an API GET to basissetexchange.org for basis set of the specified atomic numbers.
    Returns parsed response.
    """
    atomic_nos_string = ','.join(map(str, atomic_nos))
    response = requests.get(f"https://www.basissetexchange.org/api/basis/{basis_set}/format/gaussian94/?version=1&elements={atomic_nos_string}")
    if not response.ok:
        raise Exception(response.json()["message"])

    basis_set = {}
    text = response.text.split("\n")

    # print out header
    for line in text:
        if line.startswith("!"):
            _LOGGER.info(line.lstrip("!"))
        else:
            break

    # Remove header and blank lines
    text = [line for line in text if (
                line
                and not line.startswith("!")
            )]

    # iterate through the lines, make a new basis for each section of the text
    # new section denoted by "****"
    basis_lines = []
    for line in text:
        if line.startswith("*"):
            try:
                atom, orbitals = parse_basis_lines(basis_lines)
            except ValueError as e:
                _LOGGER.error(e)
                return
            basis_set[atom] = orbitals
            basis_lines = []
        else:
            basis_lines.append(line)
    return basis_set