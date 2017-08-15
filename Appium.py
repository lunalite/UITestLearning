import unittest

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
import time


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
        els = self.driver.find_elements_by_android_uiautomator('new UiSelector().clickable(true)')
        self.assertIsInstance(els, list)
        print '\n'.join(str(v) for v in els)
        action = TouchAction(self.driver)

        for btn in els:
            resourceID = btn.get_attribute('resourceId')
            action.tap(btn).perform()
            Utility.getState(self)
            Utility.back_check(self)

    def tearDown(self):
        self.driver.quit()


class Utility:
    previous_state = []
    first = True

    @staticmethod
    def back_check(_test):
        """ If no clickable, move back """
        els = _test.driver.find_elements_by_android_uiautomator('new UiSelector().clickable(true)')
        if not els:
            # _test.driver.back()
            # _test.driver.press_keycode(4)
            # time.sleep(5)
            _test.driver.press_keycode(187)

    @staticmethod
    def getState(_test):
        print 'Getting the current state...'
        els = _test.driver.find_elements_by_xpath('//*')
        els_attr = []
        for i in els:
            els_attr.append(i.get_attribute('resourceId'))

        if Utility.first:
            print 'First state'
            Utility.first = False
            Utility.previous_state = els_attr
        else:
            print 'Comparing with the previous state...'
            # print 'previous: ' + str(Utility.previous_state)
            # print 'current: ' + str(els_attr)
            result = set(Utility.previous_state) - set(els_attr)
            print result
            if not result:
                print 'same state'
            else:
                print 'different'
            Utility.previous_state = els


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ContactAppTestAppium)
    unittest.TextTestRunner(verbosity=2).run(suite)
