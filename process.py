import os
from functools import reduce
from progress.bar import Bar
from weasyprint import HTML, CSS
from yaml import safe_load, safe_dump


cssStr = """
#pre-footer, footer, header, .feedback--prompt, .feedback--yes, .feedback--no,
#hero, #user-journeys-toc, #content .track,
.docssectionheaders:last-child, .docssectionheaders:last-of-type,
.sections, #editPageButton, #docsToc, #feedback
{
    display: none !important;
}

#docsContent {
    float: none !important;
    width: 100% !important;
}

#encyclopedia {
    padding-bottom: 0 !important;
}
"""

def main():
  stream = open('./output/index.yaml')
  index = safe_load(stream)
  totalPages = reduce(lambda acc, ch: acc + len(ch['sub']) + 1, index, 0)
  bar = Bar('Processing', max=totalPages)

  try:
    os.mkdir('./output/pdf')
  except:
    pass

  for i, chapter in enumerate(index):
    bar.next()
    chapter_dir = './output/pdf/%s - %s' % (chapter['number'], chapter['title'])
    try:
      os.mkdir(chapter_dir)
    except OSError:
      pass

    if 'pdf' not in chapter:
      file_path = '%s/%s.pdf' % (chapter_dir, chapter['title'])
      html = HTML(chapter['link'])
      html.write_pdf(file_path, stylesheets=[CSS(string=cssStr)])
      index[i]['pdf'] = file_path
      store(index)

    for j, sub in enumerate(chapter['sub']):
      bar.next()
      if 'pdf' not in sub:
        sub_path = '%s/%s.pdf' % (chapter_dir, sub['title'])
        html = HTML(sub['link'])
        html.write_pdf(sub_path, stylesheets=[CSS(string=cssStr)])
        index[i]['sub'][j]['pdf'] = sub_path
        store(index)

  bar.finish()



def store(dic):
    stream = open('./output/index.yaml', 'w')
    safe_dump(dic, stream=stream, default_flow_style=False)


if __name__ == '__main__':
    main()
