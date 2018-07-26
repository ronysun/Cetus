import csv
import jinja2
import functools
import logging

LOG = logging.getLogger("testlog")

def generate_html_report(report_file, log_file, html_template):
    pass_count = 0
    failed_count = 0
    other_count = 0
    templateloader = jinja2.FileSystemLoader((html_template.split('/')[:-1]))
    templateEnv = jinja2.Environment(loader=templateloader)
    TEMPLATE_FILE = html_template.split('/')[-1]
    template = templateEnv.get_template(TEMPLATE_FILE)
    entries = []
    with open(log_file) as f:
        log_csv = csv.reader(f)
        for row in log_csv:
            try:
                if row[1] == 'p':
                    pass_count += 1
                else:
                    failed_count += 1
            except IndexError:
                other_count += 1
            entries.append(row)
        total = int(log_csv.line_num)
        data_dict = {'TOTAL': total, 'PASS': pass_count, 'FAILED': failed_count, 'OTHER': other_count, 'entries': entries}
    outputText = template.render(data_dict)
    print outputText
    report_file.write(outputText.encode('utf-8'))
    report_file.close()

def debug_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        LOG.info("function: %s -- args:  %s" % (func.__name__, kwargs))
        return func(*args, **kwargs)
    return wrapper
