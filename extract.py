#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import re
# TODO: use re.compile...


class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def process(file_, order):
    try:
        order = int(order)
    except ValueError:
        return # TODO appendices

    section_number_components = [order]
    last_n = 0
    cur_name = None
    paragraph_number = 0
    paragraph_text = ''

    with open(file_) as fp:
        for line in fp:
            m = re.search('\\\\rsec(\d?)\[(.*?)\]', line.lower())
            if m:
                n = int(m.group(1))
                if n == 0:
                    pass
                elif last_n == n:
                    section_number_components[-1] += 1
                    paragraph_number = 0
                    paragraph_text = ''
                elif last_n < n:
                    section_number_components.append(1)
                    paragraph_number = 0
                    paragraph_text = ''
                elif last_n > n:
                    for i in range(last_n - n):
                        section_number_components.pop()
                    section_number_components[-1] += 1
                name = m.group(2)
                last_n = n
                cur_name = name
            elif 'pnum' in line:
                if 'undefined' in paragraph_text and 'behavior' in paragraph_text:
                    in_code_section = False
                    par = ''
                    for par_line in paragraph_text.split('\n'):
                        if 'begin{codeblock}' in par_line:
                            in_code_section = True
                        if 'end{codeblock}' in par_line:
                            in_code_section = False
                        par += par_line + [' ', '\n'][in_code_section]
                    paragraph_text = par
                    paragraph_text = re.sub(' \\\\tcode{(.*?)}', ' \\1', paragraph_text)
                    paragraph_text = re.sub('\\\\begin{itemize}', '', paragraph_text)
                    paragraph_text = re.sub('\\\\end{itemize}', '\n', paragraph_text)
                    paragraph_text = re.sub('\\\\item', '\n  * ', paragraph_text)
                    paragraph_text = re.sub('\\\\\\\\', ' ', paragraph_text)
                    paragraph_text = re.sub('\\\\textit{(.*?)}', '\\1', paragraph_text)
                    paragraph_text = re.sub('\\\\textit{(.*?)}', '\\1', paragraph_text)
                    paragraph_text = re.sub('\\\\textit{(.*?)}', '\\1', paragraph_text)
                    paragraph_text = re.sub('\\\\ref{(.*?)}', '[\\1]', paragraph_text)
                    paragraph_text = re.sub('\\\\begin{note}', ' (note: ', paragraph_text)
                    paragraph_text = re.sub('\\\\end{note}', '-- end note) ', paragraph_text)
                    paragraph_text = re.sub('\\\\begin{codeblock}', '', paragraph_text)
                    paragraph_text = re.sub('\\\\end{codeblock}', '', paragraph_text)
                    paragraph_text = re.sub('\\\\indexlibrary{.*?}}', '', paragraph_text)
                    paragraph_text = re.sub('\\\\indextext{.*?}', '', paragraph_text)
                    paragraph_text = re.sub('\\\\indexlibrary{.*?}', '', paragraph_text)
                    paragraph_text = re.sub('\\\\\indexlibrarymember{.*?}{.*?}%', '', paragraph_text)
                    paragraph_text = re.sub('\\\\(begin{itemdecl}|end{itemdecl})', '', paragraph_text)
                    paragraph_text = re.sub('\\\\(begin{itemdescr}|end{itemdescr})', '', paragraph_text)
                    paragraph_text = re.sub('undefined', Color.RED + 'undefined' + Color.END, paragraph_text)
                    print('{0}{1}/{2} {3}{4}\n{5}\n'.format(Color.BOLD, '.'.join(map(str, section_number_components)), paragraph_number, cur_name, Color.END, paragraph_text))
                paragraph_number += 1
                paragraph_text = ''
            else:
                paragraph_text += line


def main(path):
    path = os.path.join(path, 'source')
    source_files = []
    with open(os.path.join(path, 'std.tex')) as fp:
        collect = False
        appendices = False
        order = 1
        appendix_order = 'A'
        for line in fp:
            if 'mainmatter' in line:
                collect = True
                continue
            if 'backmatter' in line:
                collect = False
                continue
            if 'appendix' in line:
                appendices = True
                continue
            if collect:
                m = re.search('\\include{(.*?)}', line)
                if not m:
                    continue
                if appendices:
                    source_files.append((appendix_order, os.path.join(path, '{}.tex'.format(m.group(1)))))
                    appendix_order = chr(ord(appendix_order) + 1)
                else:
                    source_files.append((str(order), os.path.join(path, '{}.tex'.format(m.group(1)))))
                    order += 1
    for order, file_ in source_files:
        process(file_, order)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: {} path-to-draft-repo'.format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv[1])
