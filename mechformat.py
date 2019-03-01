#!/usr/bin/env python
#
# mechformat.py
#
# Reads a mechanism file (with any tabs stripped out) and
# and reformats to a standard form for processing by chemgen.py
#
#=====================================================================================!
#                                                                                     !
#     Program:      ACCESS                                                            !
#                   Atmospheric Chemistry and Canopy Exchange Simulation System       !
#                                                                                     !
#     Version:      3.1.0                                                             !
#                                                                                     !
#     Last Update:  February 2019                                                     !
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

# Function hack to convert ACCESS/chmgen mechanism listing of reaction rate coefficients to double precision
# Listing can be entered in either single or double precision and this function
# converts each function call (up to 2 per line) to double precision arguments
# Meant to be called in chemgen.py, converting each rate coefficient string one-by-one
#  Assumptions:
#                 - No more than 2 ACCESS rate coefficient function calls in each line
#                 - No non-function parenthesis pairs occur to the left of the first
#                   function call
#                 - No variables other than "TEMP", "AIR" and "H2Oz" are passed as arguments of
#                   ACCESS rate coefficient function calls
#
def sp2dp(linesp):

    if (not linesp.startswith("kphoto")):
        linesp = linesp.upper()     # convert all alpha chars to upper case to simplify 
                                    # if the rate coefficient is not a photolysis rate
    # hack to change H2OZ to H2Oz
    ih2o = linesp.find("H2OZ")
    if (ih2o >= 0):
        llist = list(linesp)
        llist[ih2o+3] = "z"
        linesp = "".join(llist) 

    # convert line to a list of chars
    chars = []
    for c in linesp:
        chars.append(c) 

    # convert each E-scientific notation constant to D-notation
    # (i.e., x.xxE+yy to x.xxD+yy) 
    newchars = []
    i=0
    for c in chars:
        if (c == "E"):
            if (i > 0):
                # determine if this "E" is an E-scientifc notation constant or not
                # if so, convert the "E" to "D", otherwise leave it alone
                if (chars[i-1].isnumeric() or chars[i-1] == ".") and (chars[i+1].isnumeric() or chars[i+1] == "+" or chars[i+1] == "-"):
                    newchars.append("D")
                else:
                    newchars.append(c)
        else:
            newchars.append(c) 

        i+=1

    # reassemble the chars into a line
    line = "".join(newchars)

    # find first function call (if it's there)
    ileft = line.find("(")
    irght = line.find(")")

    if (ileft > -1):       # found parenthesis pair in the line
        # extract the 4 chars prior to the left parenthesis
        prefix = line[ileft-4:ileft]

        # if the prefix is one of these, then it's an ACCESS rate coefficient function call
        if (prefix == "TERM" or prefix == "TYP3" or prefix == "TYP2" or prefix == "PHO2"
               or prefix == "ERCO" or prefix == "TJPL" or prefix == " ARR" or prefix == "ARR2"):

            # extract the string between the parenthesis pair and
            #  split into a list of tokens
            plist = line[ileft+1:irght]
            slist = plist.split(",")

            # process each argument in the function call
            newslist = []
            for s in slist:
                # Any constant in scientific notation is already in D-notation, so ignore
                # Also ignore "AIR" and "TEMP" strings
                if ( (s.find("D") > 0) or (s.find("D0") > 0) or (s == "AIR") or (s == "TEMP") or (s == "H2Oz") ):
                    newslist.append(s)
                # everything else is assumed to be a decimal constant that must be
                # converted to a double precision number
                else:
                    newslist.append(s+"D0")

            # assemble new line up to the right parenthesis 
            linedp1 = line[:ileft+1]+",".join(newslist)+line[irght:irght+1]

            # rest of the input line to the right of the right parenthesis (if anything)
            line2 = line[irght+1:]

            # find second function call (if it's there)
            ileft = line2.find("(")
            irght = line2.find(")")

            if (ileft > -1):    # found a second parenthesis pair in the line
                # extract the 4 chars prior to the left parenthesis
                prefix = line2[ileft-4:ileft]

                # if the prefix is one of these, then it's an ACCESS rate coefficient function call
                if (prefix == "TERM" or prefix == "TYP3" or prefix == "TYP2" or prefix == "PHO2"
                       or prefix == "ERCO" or prefix == "TJPL" or prefix == " ARR" or prefix == "ARR2"):

                    # extract the string between the parenthesis pair and
                    #  split into a list of tokens
                    plist = line2[ileft+1:irght]
                    slist = plist.split(",")
 
                    # process each argument in the function call
                    newslist = []
                    for s in slist:
                        # Any constant in scientific notation is already in D-notation, so ignore
                        # Also ignore "AIR" and "TEMP" strings
                        if ( (s.find("D") > 0) or (s.find("D0") > 0) or (s == "AIR") or (s == "TEMP") or (s == "H2Oz") ):
                            newslist.append(s)
                        # everything else is assumed to be a decimal constant that must be
                        # converted to a double precision number
                        else:
                            newslist.append(s+"D0")

                    # assemble new second part of the line all the way to the end
                    linedp2 = line2[:ileft+1]+",".join(newslist)+line2[irght:]

                    # assemble the whole new line
                    linedp = linedp1 + linedp2 

                else:     # second parenthesis pair was not an ACCESS rate coefficient function call
                    linedp = linedp1 + line2

            else:         # no parenthesis pair in the rest of the line
                linedp = linedp1 + line2

        else:             # parenthensis pair was not an ACCESS rate coefficient function call
            linedp = line

    else:                 # no parenthesis pair in the line
        linedp = line

    return linedp

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # enforce proper usage of 2 and only 2 arguments
    if len(argv) !=3:
        print("usage: %s MECHDIR MECHFILENAME" % os.path.basename(sys.argv[0]))
        return 2

    # get filename and attach filehandle
    mechdir = argv[1]
    mechfname = argv[2]
    infile = './mechs/'+mechdir+'/'+mechfname 
    print("Reading file: %s" % infile)
    fin = open(infile)

    # read lines from infile
    lines = fin.readlines()
    fin.close()

    # open output file for reformatted mechanism
    nfchars = len(infile)
    mechname = infile[0:nfchars-4]
    outfile = './mechs/'+mechdir+'/'+'rf_'+mechdir+'.eqn'
    fout = open(outfile, 'w')
    print("Writing reformatted file: %s" % outfile)

    # write header line to reformatted file
    fout.write(lines[0])
    lines = lines[1:]

    # determine maximum length of reaction string for later formatting use
    rxnmax = 0
    for line in lines:
        icolon = line.find(":")
        if (icolon > rxnmax):
            rxnmax = icolon
    rxnmax = rxnmax+10

    # now loop over each line, split into tokens and
    # write tokens to output file in a nice easy-to-read format
    # Also, renumber reactions along the way
    rxn=0
    for line in lines:
        print(line)
        rxn+= 1
        tokens = line.split()
        icolon = tokens.index(':')
        ieol   = tokens.index(';')
        rc = ' '.join(tokens[icolon+1:ieol])
        rc = sp2dp(rc)          # convert rate coefficient expression to double precision
        rn = '{'+str(rxn)+'.}'
        fout.write(rn.ljust(8))
        ltokens = tokens[1:icolon+1]
        rxnstr = ''
        for token in ltokens:
            rxnstr+= token+' '
        fout.write(rxnstr.ljust(rxnmax))
        fout.write(rc)
        fout.write(' ;\n')

    fout.close()

    print("Success!")

    return 0

if __name__ == "__main__":
    sys.exit(main())   
