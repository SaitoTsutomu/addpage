import argparse
from importlib.metadata import metadata
from logging import INFO, StreamHandler, getLogger
from pathlib import Path

import pdfformfiller
import PyPDF2
import reportlab.lib.enums  # noqa: F401 # using in eval
from pdfformfiller import PdfFormFiller
from reportlab.lib.styles import ParagraphStyle

_package_metadata = metadata(__package__)
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")
logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(INFO)


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


def addPage(  # noqa: PLR0913, PLR0917
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
        logger.warning("Not found %s", inFile)
        return False
    if not outFile:
        outFile = inFile.with_name("out.pdf")
    alg = eval("reportlab.lib.enums.TA_" + alignment.upper())
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
    logger.info("Output %s", outFile)
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
    parser.add_argument("-a", "--alignment", default="center", choices=["center", "left", "right"])
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
