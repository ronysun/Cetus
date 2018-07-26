import sys
import os
import yaml
import time
import logging
import importlib
import common.taf_log as taf_log
import common.taf_testlink as testlink
import TestCase.config as config


test_log_name = sys.argv[1].split('.')[0]
current_time = time.strftime("-%Y-%m-%d-%H-%M-%S")
TestSuitLog = test_log_name  + current_time + ".log"
TestSuitResult = "Result-" + test_log_name  + current_time + ".csv"

logfile = logging.FileHandler("log/" + TestSuitLog)
logfile.setFormatter(logging.Formatter('%(levelname)s:%(asctime)s %(funcName)s: %(message)s'))

LOG = logging.getLogger("testlog")
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.addHandler(logfile)
LOG.setLevel(logging.DEBUG)

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
        _module_instance = importlib.import_module(_module)
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
        LOG.info('** TASK NAME: %s **', task_class_name)
        LOG.info('*' * len(task_name_info))
        case = instance_case_class(task_module_name, task_class_name)
        for tasks in d.values():
            for task in tasks:
                task_args = task.get('args')
                case.setup()
                case.run(**task_args)
                task_sla = task.get('sla')
                ((result, notes), testlink_testcase_external_id) = case.sla(**task_sla)
                RESULT.info(','.join((testlink_testcase_external_id, result, notes)))
                # report result to testlink
                tsl.report_result(testlink_testcase_external_id, result, notes)
                case.teardown()
    except IOError:
        error_message = "%s File was not found!" % casefile
        LOG.error('*' * len(error_message))
        LOG.error("%s File was not found!", casefile )
        LOG.error('*' * len(error_message))
        RESULT.info(error_message)


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

    report_file = file((test_log_name + '.html'), "w")
    taf_log.generate_html_report(report_file, TestSuitResult, config.html_template)
