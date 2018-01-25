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
parser = argparse.ArgumentParser("Print labels for dymo label writer, optionally with a qr code and an icon")
parser.add_argument('text', type=str, help="Text")
parser.add_argument('--qr', type=str, help="Text to generate a qr code for")
parser.add_argument('--icon', type=str, help="Optional png icon file")
parser.add_argument('--print', action='store_true', help="Print the label")
parser.add_argument('--output', '-o', type=str, default='label.pdf', help="Pdf output file path")
parser.add_argument('--bbox', action='store_true', help="Draw a bounding box around the label")
parser.add_argument('--noconfirm', action='store_true', help="When asked to print, just do it, don't ask for confirmation")
parser.add_argument('--preview', action='store_true', help="Show a preview of the generated pdf")
parser.add_argument('--size', type=str, default='normal', help="One of ['small', 'normal']")
parser.add_argument('--font_size', type=int, default=10)
parser.add_argument('--font', type=str, default='Helvetica')
args = parser.parse_args()


# label size
if args.size == 'normal':
    # LabelWriter 450 address labels
    LABEL_SIZE = (1.125*inch, 3.25*inch)
elif args.size == 'small':
    # small enough to fit on an akro-mils container
    LABEL_SIZE = (0.6*inch, 1.75*inch)
else:
    print("Size %s not valid" % args.size, end='')
    sys.exit(1)


# create label
c = canvas.Canvas(args.output, pagesize=LABEL_SIZE)

# transform so that we can render as if it's landscape mode
c.rotate(-90)
c.translate(-LABEL_SIZE[1], 0)

# draw qr code
qr_size = LABEL_SIZE[0]
if args.qr != None:
    qr = qrcode.make(args.qr)
    c.drawImage(ImageReader(qr._img), LABEL_SIZE[1] - qr_size, 0, qr_size, qr_size)
else:
    qr_size = 0

# draw bounding box
if args.bbox:
    c.rect(0, 0, LABEL_SIZE[1], LABEL_SIZE[0], stroke=1, fill=0)


# font
c.setFont(args.font, args.font_size)


# font metrics
def getTextHeight(fontName, fontSize):
    face = pdfmetrics.getFont(fontName).face
    ascent = (face.ascent * fontSize) / 1000.0
    descent = (face.descent * fontSize) / 1000.0

    height = ascent - descent # <-- descent it's negative
    return height

item_spacing = 4

# margins
leftMargin = 4
c.translate(leftMargin, 0)

if args.icon:
    # TODO: don't hardcode so many things
    img_width = 20
    c.drawImage(args.icon, 0, (LABEL_SIZE[0] - img_width) / 2, img_width, img_width)
    c.translate(img_width + item_spacing, 0)


# vertically centered text drawn from the current point in multiple lines so
# that it fits in the given box size
def wrappedTextBox(canvas, text, boxSize, fontName, fontSize):
    c.saveState()

    lineHeight = getTextHeight(fontName, fontSize)
    lines = simpleSplit(args.text, fontName, fontSize, textWidth)

    totalHeight = len(lines) * lineHeight

    if totalHeight > boxSize[1]:
        raise RuntimeError("ERROR: Text is too big")

    # center text vertically
    c.translate(0, (boxSize[1] - totalHeight) / 2 + totalHeight - lineHeight)

    # print each line
    for i in range(len(lines)):
        c.drawString(0, -lineHeight * i, lines[i])

    c.restoreState()

# TODO: top/bottom margin
textWidth = LABEL_SIZE[1] - qr_size - leftMargin - item_spacing
wrappedTextBox(c, args.text, (textWidth, LABEL_SIZE[0]), args.font, args.font_size)

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
