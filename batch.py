#!/usr/bin/env python3

import csv
import subprocess as proc

with open('labels.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    i = 0
    for row in reader:
        if len(row):
            # print(', '.join(row))
            # print(len(row))
            text = row[0].strip()
            icon_name = row[1].strip()
            url = 'https://shop.justbuchanan.com/inventory/%d' % i
            proc.check_call(['./main.py', '--size=small', '--out=out/%d.pdf' % i, '--bbox', '--icon=icons/%s.png' % icon_name, text, url])

        i += 1
