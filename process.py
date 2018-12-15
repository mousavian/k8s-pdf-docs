import os
from yaml import safe_load, safe_dump
from progress.bar import Bar
from weasyprint import HTML, CSS


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
  bar = Bar('Processing', max=len(index))

  try:
    os.mkdir('./output/pdf')
  except:
    pass

  for i, chapter in enumerate(index):
    if chapter['fetched'] == True:
      pass

    chapter_dir = './output/pdf/%s - %s' % (chapter['number'], chapter['title'])
    try:
      os.mkdir(chapter_dir)
    except OSError:
      pass

    file_dir = '%s/%s.pdf' % (chapter_dir, chapter['title'])
    html = HTML(chapter['link'])
    html.write_pdf(file_dir, stylesheets=[CSS(string=cssStr)])
    index[i]['fetched'] = True
    store(index)
    bar.next()
  bar.finish()



def store(dic):
    stream = open('./output/index.yaml', 'w')
    safe_dump(dic, stream=stream, default_flow_style=False)


if __name__ == '__main__':
    main()
