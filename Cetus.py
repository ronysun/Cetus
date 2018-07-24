import sys
import os
import yaml
import time
import logging
import common.taf_log as taf_log
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
                (result, notes), testlink_testcase_external_id = case.sla(**task_sla)
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

    taf_log.generate_html_report(TestSuitResult, config.html_template)
