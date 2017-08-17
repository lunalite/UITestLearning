class Utility:
    @staticmethod
    def back_check(_test):
        """ If no clickable, move back """
        els = _test.driver.find_elements_by_android_uiautomator('new UiSelector().clickable(true)')
        if not els:
            _test.driver.press_keycode(4)

    @staticmethod
    def get_state(_test, previous_state, first_state):
        same_state = False
        print 'Getting the current state...'
        els = _test.driver.find_elements_by_xpath('//*')
        els_attr = []
        for i in els:
            els_attr.append(i.get_attribute('resourceId'))

        if first_state:
            print 'First state'
            first_state = False
        else:
            print 'Comparing with the previous state...'
            # print 'previous: ' + str(Utility.previous_state)
            # print 'current: ' + str(els_attr)
            result = set(previous_state) - set(els_attr)
            print result
            if not result:
                print 'same state'
                same_state = True
            else:
                print 'different'

        previous_state = els_attr

        return first_state, previous_state, same_state

    @staticmethod
    def get_all_actions(_test, els):
        new_els = _test.driver.find_elements_by_android_uiautomator('new UiSelector().clickable(true)')
        new_els.extend(els)
        # print '\n'.join(str(v) for v in els)
        return new_els


