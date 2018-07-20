import sys
import os
import yaml
import time
import csv
import logging
from bs4 import BeautifulSoup
import common.taf_testlink as testlink
import TestCase.config as config

formatter = logging.Formatter('%(asctime)s %(funcName)s: %(message)s')
current_time = time.strftime("-%Y-%m-%d-%H-%M-%S")
TestSuitLog = "TestSuit" + current_time + ".log"
logfile = logging.FileHandler("log/" + TestSuitLog)
logfile.setFormatter(formatter)

LOG = logging.getLogger("testSuit")
LOG.addHandler(logfile)
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.setLevel(logging.INFO)

TestSuitResult = "Result" + "TestSuit" + current_time + ".csv"
result_file = logging.FileHandler("log/" + TestSuitResult)
result_file.setFormatter(logging.Formatter('%(message)s'))
RESULT = logging.getLogger("result")
RESULT.addHandler(result_file)
RESULT.setLevel(logging.INFO)

# instance Testlink connection
tsl = testlink.testlinkConnection(config.testlink_url, config.testlink_key)


def instance_case_class(module, _class_name, _module_path="TestCase"):
    _module = _module_path + "." + module
    try:
        __import__(_module)
        _module_instance = sys.modules[_module]
        _class = getattr(_module_instance, _class_name)
        case = _class()
        return case
    except ImportError:
        LOG.error("Not found module: %s, or class: %s" % (_module, _class_name))


def run_case(casefile):
    try:
        with open(casefile) as f:
            d = yaml.safe_load(f)
        casename = d.keys()[0]
        task_module_path = casename.split('.')[:-1]
        task_module_name = ".".join(task_module_path)
        task_class_name = casename.split('.')[-1]
        task_name_info = '** TASK NAME: %s **' % task_class_name
        LOG.info('*' * len(task_name_info))
        LOG.info(task_name_info)
        LOG.info('*' * len(task_name_info))
        case = instance_case_class(task_module_name, task_class_name)
        for tasks in d.values():
            for task in tasks:
                task_args = task.get('args')
                LOG.info("run task args:%s" % str(task_args))
                case.run(**task_args)
                task_sla = task.get('sla')
                LOG.info("run result check: %s" % str(task_sla))
                result, notes, testlink_testcase_external_id = case.sla(**task_sla)
                RESULT.info(','.join((testlink_testcase_external_id, result, notes)))
                # report result to testlink
                tsl.report_result(testlink_testcase_external_id, result, notes)
                case.clean_up()
    except IOError:
        error_message = "%s File was not found!" % casefile
        LOG.error('*' * len(error_message))
        LOG.error(error_message)
        LOG.error('*' * len(error_message))
        RESULT.info(error_message)


def generate_html_report(logfile, html_template=config.html_template):
    css_testlink_id = {'class': "btbg2 font-center tabtxt2", 'width': "25%%"}
    css_case_notes = {'class': 'btbg2 font-center titfont', 'width': "25%%"}
    css_case_failed = {'class': 'btbg2 font-center failedfont', 'width': "25%"}
    css_case_pass = {'class': 'btbg2 font-center passfont', 'width': "25%"}

    with open(html_template) as f:
        template = BeautifulSoup(f)
    # logfile_name = "log/" + logfile
    total = 0
    pass_count = 0
    failed_count = 0
    other_count = 0
    result_file = file("test_result.html", "w")
    with open("log/" + logfile) as l:
        log_csv = csv.reader(l)
        for row in log_csv:
            try:
                case_table_tag = template.find(id='case_table')
                new_table_entry = template.new_tag('tr')
                new_case_id_entry = template.new_tag("td", **css_testlink_id)
                if row[1] == 'p':
                    new_case_result_entry = template.new_tag("td", **css_case_pass)
                    new_case_result_entry.string = "PASS"
                    pass_count += 1
                elif row[1] == 'f':
                    new_case_result_entry = template.new_tag("td", **css_case_failed)
                    new_case_result_entry.string = "FAILED"
                    failed_count += 1
                new_case_notes_entry = template.new_tag("td", **css_case_notes)
                new_case_id_entry.string = row[0]
                new_case_notes_entry.string = row[2]
                new_table_entry.append(new_case_id_entry)
                new_table_entry.append(new_case_result_entry)
                new_table_entry.append(new_case_notes_entry)
                case_table_tag.append(new_table_entry)
            except IndexError:
                other_count += 1
                new_table_entry = template.new_tag('tr')
                new_case_id_entry = template.new_tag("td", css_testlink_id)
                new_case_id_entry.string = row[0]
                new_table_entry.append(new_case_id_entry)
                case_table_tag.append(new_table_entry)

        total = int(log_csv.line_num)
        case_count_list = [total, pass_count, failed_count, other_count]
        # init case table entry
        case_total_count_table_entry = template.new_tag("td", **css_testlink_id)
        case_pass_count_table_entry = template.new_tag("td", **css_testlink_id)
        case_failed_count_table_entry = template.new_tag("td", **css_testlink_id)
        case_other_count_table_entry = template.new_tag("td", **css_testlink_id)
        case_count_tag_list = [case_total_count_table_entry, case_pass_count_table_entry, case_failed_count_table_entry,
                               case_other_count_table_entry]

        case_count_table_tag = template.find(id="result_summary")
        case_count_entry = template.new_tag("tr")
        count_and_tag = zip(case_count_tag_list, case_count_list)

        for z in count_and_tag:
            z[0].string = str(z[1])
        for case_count_tag in case_count_tag_list:
            case_count_entry.append(case_count_tag)
        case_count_table_tag.append(case_count_entry)
        if total == pass_count + failed_count + other_count:
            print "case count is right!"
        else:
            print "case count is wrong!"

        print total, pass_count, failed_count, other_count
        result_file.write(template.prettify(encoding='utf-8'))
        result_file.close()

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        d = yaml.safe_load(f)

    if "caselist" in d.keys():
        for cases in d.values():
            for case in cases.split(' '):
                real_path = os.path.dirname(sys.argv[0]) + '/' + case
                run_case(real_path)
    else:
        run_case(sys.argv[1])

    generate_html_report(TestSuitResult)