#!/usr/bin/env python3

import qrcode
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
import argparse
import subprocess as proc
import sys

# setup command-line arguments
parser = argparse.ArgumentParser("Print labels for dymo label writer, optionally with a qr code")
parser.add_argument('text', type=str, help="Text")
parser.add_argument('qr', type=str, help="Text to generate a qr code for")
parser.add_argument('--icon', type=str, help="Optional png icon file")
parser.add_argument('--print', action='store_true', help="Print the label")
parser.add_argument('--output', '-o', type=str, default='label.pdf', help="Pdf output file path")
parser.add_argument('--bbox', action='store_true', help="Draw a bounding box around the label")
parser.add_argument('--noconfirm', action='store_true', help="When asked to print, just do it, don't ask for confirmation")
parser.add_argument('--preview', action='store_true', help="Show a preview of the generated pdf")
args = parser.parse_args()


# generate qr code
qr = qrcode.make(args.qr)
img = ImageReader(qr._img)

# TODO: make label size a cmdline arg
# LABEL_SIZE = (1.125*inch, 3.25*inch)
LABEL_SIZE = (0.6*inch, 1.75*inch)


# create label
c = canvas.Canvas(args.output, pagesize=LABEL_SIZE)

# draw qr code
c.drawImage(img, 0, 0, LABEL_SIZE[0], LABEL_SIZE[0])

# draw bounding box
if args.bbox:
    c.rect(0, 0, LABEL_SIZE[0], LABEL_SIZE[1], stroke=1, fill=0)


# font
fontName = 'Helvetica'
fontSize = 12
c.setFont(fontName, fontSize)


# font metrics
def getTextHeight(fontName, fontSize):
    face = pdfmetrics.getFont(fontName).face
    ascent = (face.ascent * fontSize) / 1000.0
    descent = (face.descent * fontSize) / 1000.0

    height = ascent - descent # <-- descent it's negative
    return height

c.translate(LABEL_SIZE[0], LABEL_SIZE[1])
c.rotate(-90)
lineSpacing = getTextHeight(fontName, fontSize)

# margins
leftMargin = 10
topMargin = 10

if args.icon:
    # TODO: don't hardcode so many things
    img_width = 20
    c.drawImage(args.icon, 4, -(LABEL_SIZE[0]*2 - img_width)/2, img_width, img_width)
    leftMargin += img_width

# TODO: right margin

c.translate(leftMargin, -topMargin)
textWidth = LABEL_SIZE[1] - LABEL_SIZE[0] - leftMargin

lines = simpleSplit(args.text, fontName, fontSize, textWidth)

totalHeight = len(lines) * lineSpacing

if totalHeight > LABEL_SIZE[0]:
    print("ERROR: Text is too big", file=sys.stderr)
    sys.exit(1)

# center text vertically
c.translate(0, -(LABEL_SIZE[0] - totalHeight) / 2)

# print each line
x = 0
for i in range(len(lines)):
    c.drawString(x, -lineSpacing*(i), lines[i])

# save label pdf file
c.save()
print("Wrote '%s'" % args.output)

if args.preview:
    proc.check_output(['xdg-open', args.output])

# print
if args.print:
    if not args.noconfirm:
        print('Confirm print: [yn] ', end='')
        response = input().lower()
        if response not in ['y', 'yes']:
            print("Cancelled, aborting print")
            sys.exit(0)

    print('Printing label...')
    proc.check_call(['lpr', args.output])
    print('Done')
