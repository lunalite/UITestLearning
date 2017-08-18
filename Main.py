from uiautomator import Device

d = Device('emulator-5554')
print d.info
d.screen.on()
d.press.home()
# d(text="Clock").click()
xml = d.dump()
print xml