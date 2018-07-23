#coding=utf-8

import testlink
import TestCase.config as config
class testlinkConnection(testlink.TestlinkAPIClient):
    def __init__(self, url, key):
        super(testlinkConnection, self).__init__(url, key)
        self.client = testlink.TestlinkAPIClient(url, key)

    def get_project_id(self, project_name):
        for project in self.client.getProjects():
            if project['name'] == project_name:
                return project['id']
        else:
            # TODO: use logmodule
            print "project: %s was not found!" % project_name

    def get_test_plan_id(self, test_plan, project_id):
        for plan in self.client.getProjectTestPlans(project_id):
            if plan['name'] == test_plan:
                return plan['id']
        else:
            # TODO: use log module
            print "test plane was not found!"

    def get_testcase_id(self, testcaseexternalid):
        return self.client.getTestCase(testcaseexternalid=testcaseexternalid)[0]['testcase_id']

    def report_result(self, testcaseexternalid, result, notes):
        testcase_id = self.get_testcase_id(testcaseexternalid)
        project_id = self.get_project_id(config.testlink_test_project_name)
        test_plan_id = self.get_test_plan_id(config.testlink_test_plan_name, project_id)
        build_name = config.testlink_build_name
        self.client.reportTCResult(testcase_id, test_plan_id, build_name, result, notes)
