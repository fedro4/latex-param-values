from math import log10, floor

# needs the xstring package to be included in the tex document for IfEqCase to work

# ... BUT IfEqCase is depressingly slow, so I switched to pdfstrcmp. apparently, this only works with pdflatex (but who uses anything else around here?), but it's much faster

# tex using IfEqCase:
#
#headertex = "\\newcommand{\\paramvalue}[2][]{\\protect\\IfEqCase{#2}{%\n"
#valtex = "\\IfEqCase{#1}{{dec}{%(decstr)s}{sci}{%(scistr)s}{dec0}{%(decstr0)s}{dec1}{%(decstr1)s}{dec2}{%(decstr2)s}}[%(defstr)s]"
#keyvaltex = "{%(keystr)s}{%(valstr)s}%%\n"
#footer1tex = "}[\PackageError{paramvalue}{unknown param name: #2}{}]}%%\n"
#footerfitex = ""
#footer2tex = ""

# tex using pdfstrcmp and nested \ifnum - \fi blocks
headertex = "\\newcommand{\\paramvalue}[2][]{\\protect %\n"
valtex =  "\\ifnum\\pdfstrcmp{#1}{dec}=0 %(decstr)s \\else\\ifnum\\pdfstrcmp{#1}{sci}=0 %(scistr)s \\else\\ifnum\\pdfstrcmp{#1}{dec0}=0 %(decstr0)s \\else\\ifnum\\pdfstrcmp{#1}{dec1}=0 %(decstr1)s \\else\\ifnum\\pdfstrcmp{#1}{dec2}=0 %(decstr2)s \\else %(defstr)s\\fi\\fi\\fi\\fi\\fi"
keyvaltex = "\\ifnum\\pdfstrcmp{#2}{%(keystr)s}=0 %(valstr)s \\else %%\n" 
footer1tex = "\\PackageError{paramvalue}{unknown param name: #2}{} %%\n"
footerfitex = "\\fi"
footer2tex = "}\n"

def rmtr(s):
    if s == "0": return s
    else: return s.rstrip('0').rstrip('.')

class LatexParamValues:
    def __init__(self):
        self.prmsets = {}

    def add(self, prmdict, prefix=None):
        if not prefix:
            prefix = len(self.prmsets.keys())
        self.prmsets[prefix] = prmdict
    
    def write(self, filename, prmdict=None):
        if prmdict is not None:
            self.add(prmdict)
        fh = open(filename, "w")

        fh.write(headertex)
        printprfx = len(self.prmsets.keys()) > 1
        num_needed_fis = 0
        for pk in self.prmsets.keys():
            prefix = str(pk) + ":" if printprfx else ""
            p = self.prmsets[pk]
            for k in p.keys():
                keystr = prefix + str(k)
                valstr = ""
                if isinstance(p[k],float):
                    # we want scientific notation, plus decimal with various formattings
                    decstr = ""
                    scistr = ""
                    e = 1
                    if p[k] == 0:
                        decstr = "0"
                        scistr = "0"
                    else:
                        e = floor(log10(abs(p[k])))
                        b = p[k]/10.**e
                        decstr = rmtr("%f" % p[k])
                        scistr = "%s \\times 10^{%s}" % (rmtr("%.2f"%b), rmtr("%.0f"%e))
                    decstr0 = "%.0f" % p[k]
                    decstr1 = rmtr("%.1f" % p[k])
                    decstr2 = rmtr("%.2f" % p[k])
                    # which one should be the default?
                    defstr = scistr if abs(e) > 3 else decstr
                    valstr = valtex % {"decstr": decstr, "scistr": scistr, "decstr0": decstr0, "decstr1": decstr1, "decstr2": decstr2, "defstr": defstr}
                else:
                    valstr = str(p[k])
                fh.write(keyvaltex % {"keystr": keystr, "valstr": valstr})
                num_needed_fis += 1
        fh.write(footer1tex)
        fh.write("".join([footerfitex for pk in range(num_needed_fis)]))
        fh.write(footer2tex)
        
        fh.close()

