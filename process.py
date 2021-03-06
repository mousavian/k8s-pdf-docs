import logging
import multiprocessing
from functools import reduce
from helpers import store_index, ensure_directory
from progress.bar import Bar
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from yaml import safe_load

font_config = FontConfiguration()
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
    logging.basicConfig(filename='process.log', level=logging.INFO)
    stream = open('./output/index.yaml')
    index = safe_load(stream)
    total_pages = reduce(lambda acc, ch: acc + len(ch['sections']) + 1, index, 0)

    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    num_consumers = multiprocessing.cpu_count() * 2
    logging.info("Creating %s consumers" % num_consumers)
    consumers = [ Converter(tasks, results) for i in range(num_consumers) ]
    bar = Bar('Downloading using %i consumers' % num_consumers, max=total_pages)
    ensure_directory('./output/pdf')
    errors_counter = 0

    for w in consumers:
        w.start()

    for chapter_number, chapter in enumerate(index):
        chapter_directory = './output/pdf/%s - %s' % (chapter['number'], chapter['title'])
        ensure_directory(chapter_directory)

        if 'pdf' in chapter:
            bar.next()
            total_pages -= 1
        elif 'error' in chapter:
            bar.next()
            total_pages -= 1
            errors_counter += 1
        else:
            tasks.put({
                'title': chapter['title'],
                'path': '%s/%s.pdf' % (chapter_directory, chapter['title'].replace('/', '-')),
                'link': chapter['link'],
                'chapter': chapter_number
            })

        for section_number, section in enumerate(chapter['sections']):
            if 'pdf' in section:
                bar.next()
                total_pages -= 1
            elif 'error' in section:
                bar.next()
                total_pages -= 1
                errors_counter += 1
            else:
                tasks.put({
                    'title': section['title'],
                    'path': ('%s/%s.pdf' % (chapter_directory, section['title'].replace('/', '-'))),
                    'link': section['link'],
                    'chapter': chapter_number,
                    'section': section_number,
                })

    # Add a poison pill for each consumer
    for i in range(num_consumers):
        tasks.put(None)

    while total_pages > 0:
        result = results.get()
        bar.next()
        logging.info("Task is done. file: %s" % (result['path']))
        is_faulty = 'error' in result
        is_section = 'section' in result
        chapter_number = result['chapter']
        if is_section:
            section_number = result['section']
            if is_faulty:
                index[chapter_number]['sections'][section_number]['error'] = True
            else:
                index[chapter_number]['sections'][section_number]['pdf'] = result['path']
        else:
            if is_faulty:
                index[chapter_number]['error'] = True
            else:
                index[chapter_number]['pdf'] = result['path']
        store_index(index)
        total_pages -= 1

    # Wait for all of the tasks to finish
    tasks.join()
    if errors_counter > 0:
        print('Got %s errors. check logs for more info' % errors_counter)
    return

class Converter(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                logging.info("%s received STOP SIGNAL." % self.name)
                self.task_queue.task_done()
                break

            section = task['section'] if 'section' in task else '-'
            logging.info("Starting to download & convert (chapter: %s/section:%s) %s" %(task['chapter'], section, task['link']))
            try:
                HTML(task['link']).write_pdf(
                    task['path'],
                    stylesheets=[CSS(string=cssStr)],
                    font_config=font_config)
            except Exception as e:
                task['error'] = True
                logging.error(e)

            self.task_queue.task_done()
            self.result_queue.put(task)
        return

if __name__ == '__main__':
    main()
