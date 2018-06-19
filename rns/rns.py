#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2018, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""
Simple tests of residue number systems. I did this mostly to build up some
intuitions for grid cells. The implementation is super inefficient.

See https://en.wikipedia.org/wiki/Residue_number_system for more details.
"""

def rnsEncode(x, moduli):
  """
  :param x: the number you want to encode
  :param moduli: a list of moduli defining this residue number system

  :return: a list of numbers representing the encoding for this RNS system
  """
  residueEncoding = []
  for m in moduli:
    residueEncoding += [x % m]
  return residueEncoding


def rnsAdd(xr, yr, moduli):
  """
  :param xr: list representing rns encoding of x using these moduli
  :param yr: list representing rns encoding of y using these moduli
  :param moduli: a list of moduli defining this residue number system

  :return: rns encoding of x+y
  """
  residueEncoding = []
  for x, y, m in zip(xr, yr, moduli):
    residueEncoding += [(x+y) % m]
  return residueEncoding


def rnsSubtract(xr, yr, moduli):
  """
  :param xr: list representing rns encoding of x using these moduli
  :param yr: list representing rns encoding of y using these moduli
  :param moduli: a list of moduli defining this residue number system

  :return: rns encoding of x-y
  """
  residueEncoding = []
  for x, y, m in zip(xr, yr, moduli):
    residueEncoding += [(x-y) % m]
  return residueEncoding


def rnsMultiply(xr, yr, moduli):
  """
  :param xr: list representing rns encoding of x using these moduli
  :param yr: list representing rns encoding of y using these moduli
  :param moduli: a list of moduli defining this residue number system

  :return: rns encoding of x*y
  """
  residueEncoding = []
  for x, y, m in zip(xr, yr, moduli):
    residueEncoding += [(x*y) % m]
  return residueEncoding


def rnsAmbiguityList(xr, xmin, xmax, moduli):
  """
  Return all integer numbers in [xmin,xmox] that have the same encoding as xr.
  An unambiguous encoding will return exactly one number (if the original number
  is in [xmin,xmox]).

  :param xr: the original encoding to compare to
  :param xmin: min range to try and encode
  :param xmax: max range to try and encode
  :param moduli: a list of moduli defining this residue number system

  :return: a list of all integer numbers in [xmin,xmox] that have the same
  encoding as xr.
  """
  ambiguousNumbers = []
  for x in range(xmin, xmax+1):
    xr2 = rnsEncode(x, moduli)
    if xr2 == xr: ambiguousNumbers += [x]

  return ambiguousNumbers


def rnsComputeAmbiguity(moduli, xmin, xmax):
  """
  Figure out the overall ambiguity of this RNS system in the 1,1000 range.

  :param moduli: a list of moduli defining this residue number system
  :param xmin: min range to try and encode
  :param xmax: max range to try and encode

  :return: a pair containing the total number of ambiguous encodings and the
  overall probability that any particular number will be ambiguous.
  """

  # Highly inefficient way of figuring this out, but hey!
  ambiguity = 0
  numAmbiguous = 0
  for i in range(xmin,xmax+1):
    ir = rnsEncode(i, moduli)
    ambiguousNumbers = rnsAmbiguityList(ir, xmin, xmax, rns)
    if len(ambiguousNumbers) > 1:
      ambiguity += len(ambiguousNumbers) - 1
      numAmbiguous += 1
      # print i, ambiguousNumbers

  return (ambiguity, float(numAmbiguous) / (xmax-xmin+1))


if __name__ == "__main__":

  rns = [3, 5, 11, 13]
  print "RNS system=",rns

  x = 20
  y = 300
  xr = rnsEncode(x, rns)
  yr = rnsEncode(y, rns)
  print "RNS encoding of x =",x,"=>", xr
  print "RNS encoding of y =",y,"=>", yr
  print
  print "Result of various operations. Here I compare RNS(f(x,y)) with "
  print "RNSf(RNS(x), RNS(y)) where RNSf() is the modulo version of f()."
  print "What we'd like to see is that the encodings of both are identical"
  print "x+y =", x+y, rnsEncode(x+y, rns), "=?", rnsAdd(xr,yr,rns)
  print "x-y =", x-y, rnsEncode(x-y, rns), "=?", rnsSubtract(xr,yr,rns)
  print "y-x =", y-x, rnsEncode(y-x, rns), "=?", rnsSubtract(yr,xr,rns)
  print "x*y =", x*y, rnsEncode(x*y, rns), "=?", rnsMultiply(xr,yr,rns)

  # A more complex equation that combines multiple functions.
  print "2x+x*y =", 2*x+x*y, rnsEncode(2*x+x*y, rns), "=?", rnsAdd(
    rnsMultiply(rnsEncode(2,rns), xr, rns),
    rnsMultiply(xr, yr, rns),rns)

  # Compute ambiguity of some rns systems

  # 3 moduli are not large enough
  rns = [5, 11, 13]
  print
  print "RNS system=",rns
  a, p = rnsComputeAmbiguity(rns, 0, 1000)
  print "Overall ambiguity for range [0,1000] =", a
  print "Probability of ambiguity =", p

  # Has 4 moduli which is better, but 12 is a multiple of 3 so not great
  rns = [3, 5, 12, 13]
  print
  print "RNS system=",rns
  a, p = rnsComputeAmbiguity(rns, 0, 1000)
  print "Overall ambiguity for range [0,1000] =", a
  print "Probability of ambiguity =", p

  # Has 4 moduli, all prime - this one is good.
  rns = [3, 5, 11, 13]
  print
  print "RNS system=",rns
  a, p = rnsComputeAmbiguity(rns, 0, 1000)
  print "Overall ambiguity for range [0,1000] =", a
  print "Probability of ambiguity =", p

  # Has 4 moduli, all prime - this one is better (smaller numbers).
  rns = [3, 5, 7, 11]
  print
  print "RNS system=",rns
  a, p = rnsComputeAmbiguity(rns, 0, 1000)
  print "Overall ambiguity for range [0,1000] =", a
  print "Probability of ambiguity =", p

  # Has 4 moduli, all increasing by sqrt(2) from a base. Works but not for
  # smaller bases
  base = 7
  rns = [base, int(round(base*1.4)), base*2, int(round(base*2.0*1.4))]
  print
  print "RNS system=",rns
  a, p = rnsComputeAmbiguity(rns, 0, 1000)
  print "Overall ambiguity for range [0,1000] =", a
  print "Probability of ambiguity =", p

