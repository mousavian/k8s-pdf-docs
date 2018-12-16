from functools import reduce
from PyPDF2 import PdfFileMerger, PdfFileReader
from yaml import safe_load


def main():
  book_path = './output/kubernetes.io-docs.pdf'
  stream = open('./output/index.yaml')
  index = safe_load(stream)

  mapped = map(to_list_of_pdf, index)
  filtered = filter(lambda x: len(x)>0, mapped)
  all_pdfs = reduce(lambda x,y: x+y, filtered, [])
  N = 50
  chunks = [all_pdfs[x:x+N] for x in range(0, len(all_pdfs), N)]
  for i, chunk in enumerate(chunks):
    merger = PdfFileMerger()
    for pdf in chunk:
      merger.append(PdfFileReader(pdf))

    with open('/tmp/k8s-doc-chunk-%s'%i, 'wb') as f:
      merger.write(f)
    merger.close()

  merger = PdfFileMerger()
  for i, chunk in enumerate(chunks):
    merger.append(PdfFileReader('/tmp/k8s-doc-chunk-%s'%i))

  with open(book_path, 'wb') as f:
      merger.write(f)
  merger.close()
  return


def to_list_of_pdf(chapter):
  pdfs = []
  pdfs += ([chapter['pdf']] if 'pdf' in chapter else [])
  pdfs += [sections['pdf'] if 'pdf' in sections else None for sections in chapter['sections']]
  return list(filter(lambda x: x is not None, pdfs))

if __name__ == '__main__':
    main()
