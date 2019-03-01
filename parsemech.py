#!/usr/bin/env python
#
# parsemech.py
#
# Reads mechanism file, determines unique species
# and creates an initial attempt at the spc file
#
#=====================================================================================!
#                                                                                     !
#     Program:      ACCESS                                                            !
#                   Atmospheric Chemistry and Canopy Exchange Simulation System       !
#                                                                                     !
#     Version:      3.1.0                                                             !
#                                                                                     !
#     Initiated:    August 2011                                                       !
#     Last Update:  August 2018                                                       !
#                                                                                     !
#     Contact:      Rick D. Saylor, PhD                                               !
#                   Physical Scientist                                                !
#                   U. S. Department of Commerce                                      !
#                   National Oceanic and Atmospheric Administration                   !
#                   Air Resources Laboratory                                          !
#                   Atmospheric Turbulence and Diffusion Division                     !
#                   456 S. Illinois Ave                                               !
#                   Oak Ridge, TN 37830                                               !
#                   email: Rick.Saylor@noaa.gov                                       !
#                   Phone: (865) 220-1730                                             !
#                                                                                     !
#=====================================================================================!
#
import os
import sys

# remove leading stoichiometric coefficients (if any) from a token
def remove_stoich(token):
    chars = list(token)
    stoich = ['0','1','2','3','4','5','6','7','8','9','.']
    n = 0
    for char in chars:
        if char in stoich:
            n+= 1
        else:
            break
    base = token[n:]
    return base 

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # enforce proper usage of 1 and only 1 argument
    if len(argv) != 2:
        print("usage: %s MECHNAME" % os.path.basename(sys.argv[0]))
        return 2

    # get filename and attach filehandle
    mechname = argv[1]
    infile = './mechs/'+mechname+'/'+mechname+'.eqn'
    print("Reading file: %s" % infile)
    f_infile = open(infile)

    # read lines from filename
    lines = f_infile.readlines()
    lines = lines[1:]  # ignore the header line
    f_infile.close()

    nfchars = len(infile)

    # loop over each line, split into tokens and add
    # to species list if unique
    specieslist = []
    for line in lines:
        tokens = line.split()
        icolon = tokens.index(':')
        tokens = tokens[1:icolon]     # ignore the reaction number and everything beyond the colon
        for token in tokens:
            base_token = remove_stoich(token)
            if base_token not in specieslist:
                specieslist.append(base_token)

    # remove operators from list
    if '+' in specieslist:
        specieslist.remove('+')
    if '-' in specieslist:
        specieslist.remove('-')
    if '->' in specieslist:
        specieslist.remove('->')
    if 'hv' in specieslist:
        specieslist.remove('hv')
    if '=' in specieslist:
        specieslist.remove('=')

    # output
    nspecies = len(specieslist)
    print("There are %s unique species in the mechanism" % nspecies)
    nsp = 0
    for species in specieslist:
        nsp += 1
        print(nsp, species)

    # write to initial stab at spc file
    if 'O2' in specieslist:
        print('removing O2 from list ...')
        specieslist.remove('O2')
    if 'H2O' in specieslist:
        print('removing H2O from list ...')
        specieslist.remove('H2O')
    if 'M' in specieslist:
        print('removing M from list ...')
        specieslist.remove('M')
    if 'CO2' in specieslist:
        print('removing CO2 from list ...')
        specieslist.remove('CO2')
    if 'H2' in specieslist:
        print('removing H2 from list ...')
        specieslist.remove('H2')
    if 'N2' in specieslist:
        print('removing N2 from list ...')
        specieslist.remove('N2')
    nfinal = len(specieslist)
    spcfname = './mechs/'+mechname+'/init_'+mechname+'.spc'
    print('Writing %d species to %s' % (nfinal, spcfname))
    spcfile = open(spcfname, 'w')
    for species in specieslist:
        spcind = species.replace('(','')
        spcind = spcind.replace(')','')
        spcfile.write('%-12s  %-12s\n' % (species, spcind))

    spcfile.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
