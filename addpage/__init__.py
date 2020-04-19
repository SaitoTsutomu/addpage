import argparse
import sys
from pathlib import Path

import pdfformfiller
import PyPDF2
from pdfformfiller import PdfFormFiller
from reportlab.lib.styles import ParagraphStyle

# see pyproject.toml
__version__ = "0.0.4"
__author__ = "Saito Tsutomu <tsutomu7@hotmail.co.jp>"


class FloatObject(PyPDF2.generic.FloatObject):
    def __add__(self, other):
        return self.as_numeric() + other

    def __radd__(self, other):
        return self.as_numeric() + other

    def __sub__(self, other):
        return self.as_numeric() - other

    def __rsub__(self, other):
        return -self.as_numeric() + other


PyPDF2.generic.FloatObject = FloatObject

pdfformfiller.__builtins__["xrange"] = range


def addPage(
    inFile,
    outFile,
    fontName,
    fontSize,
    start,
    skip,
    marginX,
    marginY,
    alignment,
    pageFormat,
):
    """Add page number to PDF file."""
    inFile = Path(inFile).resolve()
    if not inFile.exists():
        print(f"Not found {inFile}", file=sys.stderr)
        return False
    if not outFile:
        outFile = inFile.with_name("out.pdf")
    alg = eval("TA_" + alignment.upper())
    sty = ParagraphStyle("sty", alignment=alg, fontName=fontName, fontSize=fontSize)
    ff = PdfFormFiller(str(inFile))
    for i in range(ff.pdf.getNumPages()):
        if i < skip:
            continue
        p = ff.pdf.getPage(i)
        ff.add_text(
            pageFormat % (i + start - skip),
            i,
            (marginX, p.mediaBox[3] - marginY),
            (p.mediaBox[2] - marginX, p.mediaBox[3]),
            sty,
        )
    ff.write(str(outFile))
    print(f"Output {outFile}")
    return True


def main():
    parser = argparse.ArgumentParser(description=addPage.__doc__)
    parser.add_argument("infile", help="input PDF file")
    parser.add_argument("-o", "--outfile")
    parser.add_argument("-n", "--font-name", default="Helvetica")
    parser.add_argument("-z", "--font-size", type=int, default=12)
    parser.add_argument("-s", "--start", type=int, default=1)
    parser.add_argument("-k", "--skip", type=int, default=0)
    parser.add_argument("-x", "--margin-x", type=int, default=0)
    parser.add_argument("-y", "--margin-y", type=int, default=48)
    parser.add_argument(
        "-a", "--alignment", default="center", choices=["center", "left", "right"]
    )
    parser.add_argument("-f", "--format", default="- %d -")
    args = parser.parse_args()
    addPage(
        args.infile,
        args.outfile,
        fontName=args.font_name,
        fontSize=args.font_size,
        start=args.start,
        skip=args.skip,
        marginX=args.margin_x,
        marginY=args.margin_y,
        alignment=args.alignment,
        pageFormat=args.format,
    )
