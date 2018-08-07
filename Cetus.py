import sys
import os
import yaml
import time
import logging
import importlib
import common.taf_log as taf_log
import common.taf_testlink as testlink
import TestCase.config as config


cases_file_name = sys.argv[1].split('/')[-1]
test_log_name = cases_file_name.split('.')[0]
# test_log_name = sys.argv[1].split('.')[0]
current_time = time.strftime("-%Y-%m-%d-%H-%M-%S")
TestSuitLog = test_log_name  + current_time + ".log"
TestSuitResult = "Result-" + test_log_name  + current_time + ".csv"

test_log = taf_log.test_log(TestSuitLog)
result_log = taf_log.result_log(TestSuitResult)

LOG = logging.getLogger('testlog')
RESULT = logging.getLogger('result')

# instance Testlink connection
tsl = testlink.testlinkConnection(config.testlink_url, config.testlink_key)


def instance_case_class(module, _class_name, _module_path="TestCase", **kwargs):
    _module = _module_path + "." + module
    try:
        _module_instance = importlib.import_module(_module)
        _class = getattr(_module_instance, _class_name)
        case = _class(**kwargs)
        return case
    except ImportError:
        LOG.error("Not found module: %s, or class: %s" % (_module, _class_name))

def setup_test_env():
    test_image_name = 'Cetus_cirros'
    test_flavor_name = "mini.ty1"
    import TestCase.SDK.utils as SDK
    OSclient = SDK.SDKbase(admin=True)
    image = OSclient.client.get_image(test_image_name)
    if image is None:
        os.system('wget http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img -O cirros-0.3.5-x86_64-disk.img')
        OSclient._image_create(test_image_name, filename='cirros-0.3.5-x86_64-disk.img', disk_forma='qcow2')

    flavor = OSclient.client.get_flavor(test_flavor_name)
    if flavor is None:
        OSclient.client.create_flavor(test_flavor_name, 1024, 1, 40)

def run_case(casefile):
    try:
        with open(casefile) as f:
            d = yaml.safe_load(f)
        case_name = d.keys()[0]
        task_module_path = case_name.split('.')[:-1]
        task_module_name = ".".join(task_module_path)
        task_class_name = case_name.split('.')[-1]
        task_name_info = '** TASK NAME: %s **' % task_class_name
        LOG.info('*' * len(task_name_info))
        LOG.info('** TASK NAME: %s **', task_class_name)
        LOG.info('*' * len(task_name_info))
        case = instance_case_class(task_module_name, task_class_name)
        steps = d[d.keys()[0]]['steps']
        sla = d[d.keys()[0]]['sla']
        case.run(steps)
        ((result, notes), testlink_testcase_external_id) = case.sla(sla)
        RESULT.info(','.join((testlink_testcase_external_id, result, notes)))
        case.teardown()
        # report result to testlink
        tsl.report_result(testlink_testcase_external_id, result, notes)


    except IOError:
        error_message = "%s File was not found!" % casefile
        LOG.error('*' * len(error_message))
        LOG.error("%s File was not found!", casefile )
        LOG.error('*' * len(error_message))
        RESULT.info(error_message)


if __name__ == "__main__":
    if sys.argv[1] == 'init':
        setup_test_env()
    else:
        with open(sys.argv[1]) as f:
            d = yaml.safe_load(f)

        if "caselist" in d.keys():
            for cases in d.values():
                for case in cases.split(' '):
                    file_abspath = '/'.join(os.path.abspath(sys.argv[0]).split('/')[:-1])
                    real_path = file_abspath + '/' + case
                    run_case(real_path)
        else:
            run_case(sys.argv[1])

    report_file = file((test_log_name + '.html'), "w")
    result_log = "log/" + TestSuitResult
    taf_log.generate_html_report(report_file, result_log, config.html_template)
