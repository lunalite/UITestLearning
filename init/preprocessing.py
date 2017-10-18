import subprocess

x = subprocess.check_output(['ls', '/Users/hkoh006/Desktop/APK'])
x = x.split()
files = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
print(files)
counter = 0
for i in x:
    # print(i.decode('utf-8'))
    files[counter % 8].append(i.decode('utf-8'))

    counter += 1

for k, v in files.items():
    print(k, v)
    with open('/Users/hkoh006/Desktop/APK2/apk-' + str(k), 'w') as f:
        for itemz in v:
            f.write(itemz + '\n')


'''
x = subprocess.check_output(['ls', '/mnt/nas5/reps/googleplay/20170318'])
x = x.split()
files = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
print(files)
counter = 0
for i in x:
    # print(i.decode('utf-8'))
    files[counter % 8].append(i.decode('utf-8'))

    counter += 1

for k, v in files.items():
    print(k, v)
    with open('/home/hongda/Document/apk/apk-' + str(k), 'w') as f:
        for itemz in v:
            f.write(itemz + '\n')
'''