"""
Currently, appium automated test is made just for clickable buttons.
"""

import unittest

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction

from old2.Utility import Utility


class ContactAppTestAppium(unittest.TestCase):
    def setUp(self):
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '8.0'
        desired_caps['deviceName'] = 'A102'
        # desired_caps['app'] = '/Users/chaosluna/Desktop/aaa/AppiumDemoWithPython/src/WitStatus.apk'
        desired_caps['app'] = '/Users/chaosluna/Desktop/aaa/AppiumDemoWithPython/src/app-debug2.apk'
        # desired_caps['appPackage'] = 'com.witmergers.getstatus'
        # desired_caps['appActivity'] = '.MainActivity'

        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)

    def test_findClickableButtons(self):
        previous_state = []
        els = []
        first_state = True
        action = TouchAction(self.driver)

        first_state, previous_state, same_state = Utility.get_state(self, previous_state, first_state)

        while True:
            if not same_state:
                els = Utility.get_all_actions(self, els)
            print els
            if els:
                action.tap(els.pop(0)).perform()
                # resourceID = btn.get_attribute('resourceId')
                first_state, previous_state, same_state = Utility.get_state(self, previous_state, first_state)
                Utility.back_check(self)
            else:
                print 'break'
                break
        print 'not done yet'

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ContactAppTestAppium)
    unittest.TextTestRunner(verbosity=2).run(suite)
