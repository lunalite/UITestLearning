import codecs
import random
import sys

import numpy as np
import tensorflow as tf
from tqdm import *

grams = 1
suffix = ''
treat_as_individual_word = False
treat_all_null_as_invalid = False
learning_method = ''
try:
    grams = int(sys.argv[1])
    if sys.argv[2] == '00':
        pass
    elif sys.argv[2] == '01':
        suffix = 'in'
        treat_all_null_as_invalid = True
    elif sys.argv[2] == '10':
        suffix = 'iw'
        treat_as_individual_word = True
    elif sys.argv[2] == '11':
        suffix = 'iwin'
        treat_as_individual_word = True
        treat_all_null_as_invalid = True
    else:
        raise ValueError
    if sys.argv[3] in ['w', 'd', 'wnd']:
        learning_method = sys.argv[3]
    else:
        raise ValueError
except IndexError:
    print('Please enter arguments:')
    print('argv[1] == n: n-gram.')
    print('argv[2] == 10/00: Treating individual word or not.')
    print('argv[2] == 11/01: Treat all null sequence as invalid.')
    print('argv[3] == w/d/wnd: wide/deep/widendeep training method')
    exit(1)
except ValueError:
    print('Please enter a right value argument')
    print('argv[1] == n: n-gram.')
    print('argv[2] == 10/00: Treating individual word or not.')
    print('argv[2] == 11/01: Treat all null sequence as invalid.')
    print('argv[3] == w/d/wnd: wide/deep/widendeep training method')
    exit(1)

category = ['TOOLS', 'GAME_SIMULATION', 'GAME_WORD', 'PERSONALIZATION', 'MEDIA_AND_VIDEO', 'SHOPPING',
            'GAME_ROLE_PLAYING', 'PRODUCTIVITY', 'GAME_EDUCATIONAL', 'GAME_ACTION', 'SOCIAL', 'NEWS_AND_MAGAZINES',
            'GAME_ARCADE', 'GAME_CASINO', 'HEALTH_AND_FITNESS', 'LIFESTYLE', 'PHOTOGRAPHY', 'GAME_STRATEGY',
            'COMMUNICATION', 'GAME_ADVENTURE', 'GAME_CARD', 'GAME_BOARD', 'TRANSPORTATION', 'GAME_MUSIC', 'BUSINESS',
            'GAME_CASUAL', 'SPORTS', 'GAME_RACING', 'FINANCE', 'TRAVEL_AND_LOCAL', 'MUSIC_AND_AUDIO',
            'LIBRARIES_AND_DEMO', 'WEATHER', 'BOOKS_AND_REFERENCE', 'ENTERTAINMENT', 'EDUCATION', 'GAME_PUZZLE',
            'GAME_TRIVIA', 'MEDICAL', 'COMICS', 'GAME_SPORTS', '#']

btnclass = ['ViewPager', 'ViewAnimator', 'RelativeLayout', 'ActionBar$Tab', 'HorizontalListView', 'TableLayout',
            'WebView', 'dd', 'da', 'HorizontalScrollView', 'd', 'SeekBar', 'CheckedFrameLayout', 'ImageButton',
            'RecycleDataViewGroup', 'MenuItem', 'TextView', 'CheckBox', 'EditText', 'SearchView', 'FrameLayout',
            'GridLayout', 'ViewGroup', 'MultiAutoCompleteTextView', 'TwoWayView', 'ViewFlipper', 'TextInputLayout',
            'ZoomButton', 'a$c', 'bg', 'ScrollView', 'bp', 'ActionBar$c', 'ActionBar$a', 'ImageView', 'HListView',
            'TableRow', 'Image', 'ProgressBar', 'ActionBar$b', 'ci', 'ch', 'ji$c', 'Spinner', 'cz', 'cy', 'cs', 'ag',
            'TwoLineListItem', 'ListView', 'DigitalClock', 'c', 'Switch', 'RecyclerView', 'CompoundButton', 'b', 'uq',
            'a$f', 'TextSwitcher', 'a$d', 'TimePicker', 'a$b', 'SwitchCompat', 'ViewSwitcher', 'ai', 'ak', 'aj', 'am',
            'al', 'ao', 'an', 'aq', 'ap', 'as', 'ar', 'RadioGroup', 'ay', 'ImageSwitcher', 'ToggleButton', 'VideoView',
            'Gallery', 'LinearLayoutCompat', 'Button', 'RadioButton', 'Chronometer', 'DrawerLayout', 'LinearLayout',
            'CheckedTextView', 'View', 'e', 'RatingBar', 'NA']

position = ['-1', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']

lstmUnits = 64
numDimensions = 50
batch_size = 24

maxDSeqLength = grams * 3 if 'iw' in suffix else grams
maxSeqLength = 3

wordVector = np.load('../data/wordVector' + str(grams) + suffix + '.npy')

"""Populating model"""

print('\nPopulating sequence and label...')
try:
    wids = np.load('../data/widslabel' + str(grams) + suffix + '.npy')
    dlabellist = np.load('../data/dlabellist' + str(grams) + suffix + '.npy')
    dids = np.load('../data/didslabel' + str(grams) + suffix + '.npy')
    # assert len(wids) * 24 == len(dlabellist) == len(dids) * 24
except FileNotFoundError:
    wids = []
    dids = []
    dlabellist = []

if len(wids) == 0:
    ''' Populate the model and save it into .npy file for faster learning in the future. '''
    print('Loading model and saving it into .npy files...')
    data = []
    wordList = np.load('../data/wordList' + str(grams) + suffix + '.npy')
    wordList = wordList.tolist()
    with codecs.open('../data/datawide-gram' + str(grams) + suffix + '.txt', 'r', 'utf-8') as f:
        wlines = [x.strip() for x in f.readlines()]
    with codecs.open('../data/dataseq-gram' + str(grams) + suffix + '.txt', 'r', 'utf-8') as f:
        dlines = [x.strip('\n') for x in f.readlines()]

    wbatch_ids = np.zeros((batch_size, maxSeqLength), dtype='int32')
    dnp_arr = np.zeros([batch_size, maxDSeqLength])
    fileCounter = 0

    assert len(wlines) == len(dlines)

    for no in tqdm(range(len(wlines))):
        # If wlsplit is None, means action in sequence ends with not a button (can be a random button, or close)
        wlsplit = wlines[no].split(':::', 1)
        dlsplit = dlines[no].split(':::', 1)

        if len(wlsplit) == 1:
            continue
        else:
            ssplit = wlsplit[1].split('\t')
            assert len(ssplit) == 3
            try:
                if len(dlsplit) == 2:
                    if dlsplit[0] == 'positive':
                        dlabellist.append([1, 0])
                    elif dlsplit[0] == 'negative':
                        dlabellist.append([0, 1])
                    else:
                        if no + 24 > len(wlines):
                            break
                        continue
                else:
                    print(dlsplit)
                    exit(1)

                wbatch_ids[fileCounter][0] = category.index(ssplit[0])
                try:
                    wbatch_ids[fileCounter][1] = btnclass.index(ssplit[1])
                except Exception:
                    wbatch_ids[fileCounter][1] = btnclass.index('NA')
                wbatch_ids[fileCounter][2] = position.index(ssplit[2])

                displit = dlsplit[1].split('\t')
                dindexCounter = 0
                for section in displit:
                    dnp_arr[fileCounter][dindexCounter] = wordList.index(section)
                    dindexCounter += 1
                    if dindexCounter >= maxDSeqLength:
                        break
                fileCounter += 1
            except ValueError as e:
                print(e)
                exit(1)

        if fileCounter >= batch_size:
            wids.append(wbatch_ids)
            dids.append(dnp_arr)
            fileCounter = 0
            wbatch_ids = np.zeros((batch_size, maxSeqLength), dtype='int32')
            dnp_arr = np.zeros([batch_size, maxDSeqLength])
            try:
                assert len(dlabellist) == len(dids) * 24 == len(wids) * 24
            except Exception:
                print(len(dlabellist))
                print(len(dids) * 24)
                print(len(wids) * 24)
                exit(1)

            if no + 24 > len(wlines):
                break

    np.save('../data/widslabel' + str(grams) + suffix, wids)
    np.save('../data/dlabellist' + str(grams) + suffix, dlabellist)
    np.save('../data/didslabel' + str(grams) + suffix, dids)
    """End populating model"""

no_train_data_batch = int(len(wids) * 9 / 10)
no_test_data_batch = len(wids) - no_train_data_batch

train_wids = wids[:no_train_data_batch]
test_wids = wids[no_train_data_batch:]
train_labels = dlabellist[:no_train_data_batch * 24]

train_dids = dids[:no_train_data_batch]
test_dids = dids[no_train_data_batch:]
test_labels = dlabellist[no_train_data_batch * 24:]

combination_train = []
for i in range(len(train_wids)):
    combination_train.append((train_wids[i], train_dids[i], train_labels[i * 24:(i + 1) * 24]))

print('Number of training data batch: %d.' % no_train_data_batch)
print('Number of test data batch: %d.' % no_test_data_batch)
print('Length of deep labels: %s' % len(dlabellist))
print('Length of deep ids: %s' % len(dids))
print('Length of wide ids: %s' % len(wids))

tf.reset_default_graph()

print('Undergoing %s model training.' % learning_method)

if learning_method == 'w':
    ''' Wide model '''
    learning_rate = 0.1
    training_epochs = 1
    wide_input = tf.placeholder(tf.float32, [None, 3])
    deep_label = tf.placeholder(tf.float32, [None, 2])
    W = tf.Variable(tf.zeros([3, 2]))
    b = tf.Variable(tf.zeros([2]))
    wide_pred = (tf.matmul(wide_input, W) + b)

    # cost = tf.reduce_mean(-tf.reduce_sum(deep_label * tf.log(wide_pred), reduction_indices=1))
    cost = tf.nn.softmax_cross_entropy_with_logits_v2(logits=wide_pred, labels=deep_label)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

if learning_method == 'd':
    ''' Deep model '''
    training_epochs = 1
    deep_label = tf.placeholder(tf.float32, [None, 2])
    deep_input = tf.placeholder(tf.int32, [None, maxDSeqLength])

    data = tf.Variable(tf.zeros([batch_size, maxDSeqLength, numDimensions]), dtype=tf.float32)  # (24x[grams*3]x150)
    data = tf.nn.embedding_lookup(wordVector, deep_input)

    lstmCell = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
    lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=0.75)
    value, _ = tf.nn.dynamic_rnn(lstmCell, data, dtype=tf.float32)

    weight = tf.Variable(tf.truncated_normal([lstmUnits, 2]))
    bias = tf.Variable(tf.constant(0.1, shape=[2]))
    value = tf.transpose(value, [1, 0, 2])
    last = tf.gather(value, int(value.get_shape()[0]) - 1)
    deep_pred = tf.nn.relu(tf.matmul(last, weight) + bias)

    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=deep_pred, labels=deep_label))
    optimizer = tf.train.AdamOptimizer().minimize(loss)

if learning_method == 'wnd':
    ''' Wide and Deep model '''
    training_epochs = 1
    intermediate_size = 2

    wide_input = tf.placeholder(tf.float32, [None, 3])
    W = tf.Variable(tf.zeros([3, intermediate_size]))
    b = tf.Variable(tf.constant(0.1, shape=[intermediate_size]))
    wide_pred = tf.nn.relu(tf.matmul(wide_input, W) + b)

    deep_label = tf.placeholder(tf.float32, [None, 2])
    deep_input = tf.placeholder(tf.int32, [None, maxDSeqLength])

    data = tf.Variable(tf.zeros([batch_size, maxDSeqLength, numDimensions]), dtype=tf.float32)
    data = tf.nn.embedding_lookup(wordVector, deep_input)

    lstmCell = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
    lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=0.75)
    value, _ = tf.nn.dynamic_rnn(lstmCell, data, dtype=tf.float32)

    weight = tf.Variable(tf.truncated_normal([lstmUnits, intermediate_size]))
    bias = tf.Variable(tf.constant(0.1, shape=[intermediate_size]))
    value = tf.transpose(value, [1, 0, 2])
    last = tf.gather(value, int(value.get_shape()[0]) - 1)
    deep_pred = tf.nn.relu(tf.matmul(last, weight) + bias)

    ''' Combining both wide and deep '''
    weighted_pred = wide_pred + deep_pred

    ''' Adding additional layer '''
    w1 = tf.Variable(tf.random_normal([intermediate_size, 2]))
    b1 = tf.Variable(tf.constant(0.1, shape=([2])))
    new_prediction = tf.nn.softmax(tf.matmul(weighted_pred, w1) + b1)
    test_new_prediction = tf.matmul(weighted_pred, w1) + b1

    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=new_prediction, labels=deep_label))
    optimizer = tf.train.AdamOptimizer().minimize(loss)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:
    # Run the initializer
    sess.run(init)

    # Training cycle
    for epoch in range(training_epochs):
        # Loop over all batches
        if learning_method == 'w':
            avg_cost = 0.
            for i in tqdm(range(no_train_data_batch)):
                train_wide_input, train_deep_input, train_label = random.choice(combination_train)
                sess.run(optimizer, feed_dict={wide_input: train_wide_input, deep_label: train_label})
        elif learning_method == 'd':
            for i in tqdm(range(no_train_data_batch)):
                train_wide_input, train_deep_input, train_label = random.choice(combination_train)
                sess.run(optimizer, feed_dict={deep_input: train_deep_input, deep_label: train_label})
        elif learning_method == 'wnd':
            for i in tqdm(range(no_train_data_batch)):
                train_wide_input, train_deep_input, train_label = random.choice(combination_train)
                sess.run(optimizer, feed_dict={wide_input: train_wide_input, deep_input: train_deep_input,
                                               deep_label: train_label})

    print("Optimization Finished!")

    training_result = []

    # Test model
    if learning_method == 'w':
        correct_prediction = tf.equal(tf.argmax(wide_pred, 1), tf.argmax(deep_label, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        for i in tqdm(range(no_test_data_batch)):
            test_label = test_labels[i * 24: (i + 1) * 24]
            test_wide_input = test_wids[i]
            result = sess.run(accuracy, feed_dict={wide_input: test_wide_input, deep_label: test_label})
            training_result.append(result)

    elif learning_method == 'd':
        correct_prediction = tf.equal(tf.argmax(deep_pred, 1), tf.argmax(deep_label, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        for i in tqdm(range(no_test_data_batch)):
            test_label = test_labels[i * 24: (i + 1) * 24]
            test_deep_input = test_dids[i]
            result = sess.run(accuracy, feed_dict={deep_input: test_deep_input, deep_label: test_label})
            training_result.append(result)

    elif learning_method == 'wnd':
        correct_prediction = tf.equal(tf.argmax(test_new_prediction, 1), tf.argmax(deep_label, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        for i in tqdm(range(no_test_data_batch)):
            test_label = test_labels[i * 24: (i + 1) * 24]
            test_wide_input = test_wids[i]
            test_deep_input = test_dids[i]
            result = sess.run(accuracy,
                              feed_dict={wide_input: test_wide_input, deep_input: test_deep_input,
                                         deep_label: test_label})
            training_result.append(result)

    final_acc = sum(training_result) / len(training_result)
    print('Final accuracy: %f ' % final_acc)

    with open('./tstresult.txt', 'a') as f:
        f.write(
            'final_accuracy: %s for %d-gram, iw: %s and in: %s with no_train_data: %s, no_test_data: %s, '
            'learning_rate: %s, batch_size: %s using %s model \n' % (
                final_acc, grams, treat_as_individual_word, treat_all_null_as_invalid, no_train_data_batch,
                no_test_data_batch, learning_rate, batch_size, learning_method))
