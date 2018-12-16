import glob
from functools import reduce
from PyPDF2 import PdfFileMerger, PdfFileReader
from yaml import safe_load


def main():
  book_path = './output/kubernetes.io-docs.pdf'
  stream = open('./output/index.yaml')
  index = safe_load(stream)
  merger = PdfFileMerger()

  mapped = map(to_list_of_pdf, index)
  filtered = filter(lambda x: len(x)>0, mapped)
  all_pdfs = reduce(lambda x,y: x+y, filtered, [])

  for pdf in all_pdfs:
    merger.append(PdfFileReader(pdf))

  with open(book_path, 'wb') as f:
    merger.write(f)

def to_list_of_pdf(chapter):
  pdfs = []
  pdfs += ([chapter['pdf']] if 'pdf' in chapter else [])
  pdfs += [sub['pdf'] if 'pdf' in sub else None for sub in chapter['sub']]
  return list(filter(lambda x: x is not None, pdfs))

if __name__ == '__main__':
    main()
