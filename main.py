#!/usr/bin/env python3

import qrcode
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import argparse
import subprocess as proc

# setup command-line arguments
parser = argparse.ArgumentParser("Print labels for dymo label writer, optionally with a qr code")
parser.add_argument('text', type=str, help="Text")
parser.add_argument('qr', type=str, help="Text to generate a qr code for")
parser.add_argument('--print', action='store_true', help="Print the label")
args = parser.parse_args()


# generate qr code
qr = qrcode.make(args.qr)
img = ImageReader(qr._img)


# units
point = 1
inch = 72 * point
LABEL_SIZE = (1.125*inch, 3.25*inch)


# create label
outfile = "label.pdf"
c = canvas.Canvas(outfile, pagesize=LABEL_SIZE)
c.drawImage(img, 0, 0, LABEL_SIZE[0], LABEL_SIZE[0])
# canvas.setFont('Times-Roman', 9) 
c.translate(0, LABEL_SIZE[1])
c.rotate(-90)
c.drawString(10, 10, args.text)


c.save()

# print
if args.print:
    print('Printing label...')
    proc.check_call(['lpr', outfile])
    print('Done')
