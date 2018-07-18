import sys
import yaml
import time
import logging
import common.taf_testlink as testlink
import TestCase.config as config


LOG = logging.getLogger("testSuit")
formatter = logging.Formatter('%(asctime)s%(levelname)-8s: %(message)s')
TestSuitLog = "TestSuit" + time.strftime("-%Y-%m-%d-%H-%M-%S") + ".log"
logfile = logging.FileHandler("log/"+TestSuitLog)
logfile.setFormatter(formatter)

# instance Testlink connection
tsl = testlink.testlinkConnection(config.testlink_url, config.testlink_key)

LOG.addHandler(logfile)
LOG.setLevel(logging.INFO)

def instance_case_class(module, _class_name, _module_path="TestCase"):
    _module = _module_path + "." + module
    try:
        __import__(_module)
        _module_instance = sys.modules[_module]
        _class = getattr(_module_instance, _class_name)
        case = _class()
        return case
    except ImportError:
        print "Not found class"


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        f = open(sys.argv[1])
    d = yaml.safe_load(f)
    casename = d.keys()[0]
    task_module_path = casename.split('.')[:-1]
    task_module_name = ".".join(task_module_path)
    task_class_name = casename.split('.')[-1]
    case = instance_case_class(task_module_name, task_class_name)
    for tasks in d.values():
        for task in tasks:
            task_args = task.get('args')
            # LOG.info("run task args:%s" % str(task_args))
            case.run(**task_args)
            task_sla = task.get('sla')
            result, notes, testcase_external_id = case.sla(**task_sla)
            tsl.report_result(testcase_external_id, result, notes)
            case.clean_up()
