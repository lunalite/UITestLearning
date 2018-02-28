import random

import numpy as np
import codecs
import tensorflow as tf
import sys
from tqdm import *

category = ['TOOLS', 'GAME_SIMULATION', 'GAME_WORD', 'PERSONALIZATION', 'MEDIA_AND_VIDEO', 'SHOPPING',
            'GAME_ROLE_PLAYING', 'PRODUCTIVITY', 'GAME_EDUCATIONAL', 'GAME_ACTION', 'SOCIAL', 'NEWS_AND_MAGAZINES',
            'GAME_ARCADE', 'GAME_CASINO', 'HEALTH_AND_FITNESS', 'LIFESTYLE', 'PHOTOGRAPHY', 'GAME_STRATEGY',
            'COMMUNICATION', 'GAME_ADVENTURE', 'GAME_CARD', 'GAME_BOARD', 'TRANSPORTATION', 'GAME_MUSIC', 'BUSINESS',
            'GAME_CASUAL', 'SPORTS', 'GAME_RACING', 'FINANCE', 'TRAVEL_AND_LOCAL', 'MUSIC_AND_AUDIO',
            'LIBRARIES_AND_DEMO', 'WEATHER', 'BOOKS_AND_REFERENCE', 'ENTERTAINMENT', 'EDUCATION', 'GAME_PUZZLE',
            'GAME_TRIVIA', 'MEDICAL', 'COMICS', 'GAME_SPORTS', '#']

btnclass = ['TimePicker', 'e', 'WebView', 'HorizontalListView', 'ViewPager', 'ViewGroup', 'ImageButton', 'DrawerLayout',
            'ak', 'ImageView', 'MultiAutoCompleteTextView', 'RadioGroup', 'da', 'TableLayout', 'TwoLineListItem',
            'TextView', 'ai', 'Image', 'a$f', 'd', 'EditText', 'HorizontalScrollView', 'SeekBar', 'View', 'CheckBox',
            'dd', 'ImageSwitcher', 'TableRow', 'ViewSwitcher', 'CheckedFrameLayout', 'Switch', 'HListView', 'ci',
            'ScrollView', 'SearchView', 'ActionBar$a', 'ActionBar$b', 'CheckedTextView', 'ProgressBar', 'TwoWayView',
            'SwitchCompat', 'TextInputLayout', 'cs', 'c', 'RecyclerView', 'ar', 'ViewFlipper', 'ap', 'GridLayout', 'aj',
            'LinearLayout', 'ch', 'Button', 'a$d', 'RadioButton', 'a$c', 'ToggleButton', 'MenuItem', 'Gallery', 'ao',
            'Spinner', 'an', 'VideoView', 'b', 'DigitalClock', 'ji$c', 'am', 'a$b', 'CompoundButton', 'ActionBar$Tab',
            'ZoomButton', 'cz', 'RelativeLayout', 'al', 'aq', 'ListView', 'RatingBar', 'ActionBar$c', 'FrameLayout',
            'ag', 'LinearLayoutCompat']

position = ['-1', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']

batch_size = 24
treat_as_individual_word = False
treat_all_null_as_invalid = False
suffix = ''
data = []
maxSeqLength = 3
no_train_data_batch = 0
no_test_data_batch = 0
idslabel = []
train_idslabel = []
test_idslabel = []
batch_labels = []
compressed_test_ids = []
compressed_test_label = []

try:
    grams = int(sys.argv[1])
    if sys.argv[2] == '10':
        suffix = 'iw'
        treat_as_individual_word = True
    elif sys.argv[2] == '00':
        pass
    elif sys.argv[2] == '11':
        suffix = 'iwin'
        treat_as_individual_word = True
        treat_all_null_as_invalid = True
    elif sys.argv[2] == '01':
        suffix = 'in'
        treat_all_null_as_invalid = True
except IndexError:
    print('Please enter arguments:')
    print('argv[1] == n: n-gram.')
    print('argv[2] == 10/00: Treating individual word or not.')
    print('argv[2] == 11/01: Treat all null sequence as invalid.')
    exit(1)
idsMatrixFile = '../data/idsMatrix' + str(grams) + suffix + '.npy'
wordList = np.load('../data/wordList' + str(grams) + suffix + '.npy')
wordList = wordList.tolist()
wordVector = np.load('../data/wordVector' + str(grams) + suffix + '.npy')


def populate_model():
    global batch_labels, idslabel, compressed_test_ids, compressed_test_label, test_idslabel, train_idslabel
    with codecs.open('../data/datawide-gram' + str(grams) + suffix + '.txt', 'r') as f:
        lines = [x.strip() for x in f.readlines()]

    batch_ids = np.zeros((batch_size, maxSeqLength), dtype='int32')
    fileCounter = 0

    for line in lines:
        lsplit = line.split(':::')
        if len(lsplit) == 1:
            pass
        else:
            ssplit = lsplit[1].split('\t')
            assert len(ssplit) == 3
            try:
                batch_ids[fileCounter][0] = category.index(ssplit[0])
                batch_ids[fileCounter][1] = btnclass.index(ssplit[1])
                batch_ids[fileCounter][2] = position.index(ssplit[2])
                fileCounter += 1
            except ValueError:
                continue
            if lsplit[0] == 'positive':
                batch_labels.append([1, 0])
            elif lsplit[0] == 'negative':
                batch_labels.append([0, 1])
            else:
                print('Error: Not positive, negative label.')
                exit(1)
        if len(batch_labels) >= batch_size:
            # if len(batch_labels) != fileCounter:
            #     break
            idslabel.append((batch_ids, batch_labels))
            fileCounter = 0
            batch_labels = []
            batch_ids = np.zeros((batch_size, maxSeqLength), dtype='int32')

    no_train_data_batch = int(len(idslabel) * 9 / 10)
    no_test_data_batch = len(idslabel) - no_train_data_batch
    random.shuffle(idslabel)
    train_idslabel = idslabel[:no_train_data_batch]
    test_idslabel = idslabel[no_train_data_batch:]
    # compressed_test_ids = np.zeros((batch_size * len(test_idslabel), maxSeqLength), dtype='int32')

    print('Number of training data batch: %d.' % no_train_data_batch)
    print('Number of test data batch: %d.' % no_test_data_batch)

    # fileCounter = 0
    # for j in test_idslabel:
    #     indexCounter = 0
    #     for k in j[0]:
    #         compressed_test_ids[fileCounter * 24 + indexCounter] = k
    #         indexCounter += 1
    #     compressed_test_label[fileCounter * 24: fileCounter * 24 + 24] = j[1]
    #     fileCounter += 1


populate_model()

# # Parameters
learning_rate = 0.5
training_epochs = 10
display_step = 1

tf.reset_default_graph()

# tf Graph Input
x = tf.placeholder(tf.float32, [None, 3])
y = tf.placeholder(tf.float32, [None, 2])

# Set model weights
W = tf.Variable(tf.zeros([3, 10]))
b = tf.Variable(tf.zeros([10]))

# Construct model
wide_pred = tf.nn.relu(tf.matmul(x, W) + b)  # Softmax (24,3) x (3,2) = (24x2) + (1x2) = (24x2)

# Minimize error using cross entropy
# cost = tf.reduce_mean(-tf.reduce_sum(y * tf.log(pred), reduction_indices=1))

"""
============================================================
"""
lstmUnits = 64
numClasses = 2
numDimensions = 50
labellist = []
sequencelist = []
ids = np.load(idsMatrixFile)
maxDSeqLength = grams * 3

with codecs.open('../data/dataseq-gram' + str(grams) + suffix + '.txt', 'r', 'utf-8') as f:
    lines = [x.strip('\n') for x in f.readlines()]


def populate_seqlab():
    print('\nPopulating sequence and label...')

    for i in tqdm(range(len(lines))):
        lsplit = lines[i].split(':::')
        if len(lsplit) == 2:
            labellist.append(lsplit[0])
            sequencelist.append(lsplit[1])
        else:
            sequencelist[-1] += '\n' + lines[i]

    print('Length of labels: %s' % len(labellist))
    print('Length of sequence: %s' % len(sequencelist))
    return len(labellist)


number_of_data = populate_seqlab()


def getTrainBatch(ids, _i):  # returns 24,9 arr and 24,2 label
    _labels = []
    np_arr = np.zeros([batch_size, maxDSeqLength])
    i = 0
    num = _i * batch_size
    max_num = int(9 / 10 * number_of_data)
    assert num < int(9 / 10 * number_of_data)
    while i < batch_size:
        # num = random.randint(1, int(9 / 10 * number_of_data))
        if num >= max_num:
            break
        if labellist[num] == 'positive':
            _labels.append([1, 0])
        elif labellist[num] == 'negative':
            _labels.append([0, 1])
        else:
            num += 1
            continue
        np_arr[i] = ids[num:num + 1]
        i += 1
    return np_arr, _labels


def getTestBatch(ids, _i):
    _labels = []
    arr = np.zeros([batch_size, maxDSeqLength])
    i = 0
    num = int(9 / 10 * number_of_data) + _i * batch_size
    try:
        while i < batch_size:
            if labellist[num] == 'positive':
                _labels.append([1, 0])
            elif labellist[num] == 'negative':
                _labels.append([0, 1])
            else:
                num += 1
                continue
            arr[i] = ids[num: num + 1]
            i += 1
            num += 1
        return arr, _labels
    except IndexError:
        return None, None


labels = tf.placeholder(tf.float32, [None, numClasses])
input_data = tf.placeholder(tf.int32, [None, maxDSeqLength])

data = tf.Variable(tf.zeros([batch_size, maxDSeqLength, numDimensions]), dtype=tf.float32)  # (24x[grams*3]x150)
data = tf.nn.embedding_lookup(wordVector, input_data)

lstmCell = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=0.75)
value, _ = tf.nn.dynamic_rnn(lstmCell, data, dtype=tf.float32)

weight = tf.Variable(tf.truncated_normal([lstmUnits, 10]))
bias = tf.Variable(tf.constant(0.1, shape=[10]))
value = tf.transpose(value, [1, 0, 2])
last = tf.gather(value, int(value.get_shape()[0]) - 1)
deep_pred = tf.nn.relu(tf.matmul(last, weight) + bias)

# correctPred = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
# accuracy = tf.reduce_mean(tf.cast(correctPred, tf.float32))

"""
============================================================
"""
weighted_pred = wide_pred + deep_pred

w1 = tf.Variable(tf.random_normal([10, 2]))
b1 = tf.Variable(tf.zeros([2]))
new_prediction = tf.nn.softmax(tf.matmul(weighted_pred, w1) + b1)

# cost = tf.reduce_mean(-tf.reduce_sum(y * tf.log(weighted_pred)))
cost = tf.reduce_mean(-tf.reduce_sum(y * tf.log(new_prediction)))
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:
    # Run the initializer
    sess.run(init)

    # Training cycle
    for epoch in range(training_epochs):
        avg_cost = 0.

        # Loop over all batches
        for i in range(no_train_data_batch):
            # Run optimization op (backprop) and cost op (to get loss value)
            # _, c = sess.run(optimizer, feed_dict={x: train_idslabel[i][0], input_data: getTrainBatch(ids, i)[0],
            #                                       y: train_idslabel[i][1]})
            _, c = sess.run(optimizer, feed_dict={x: train_idslabel[i][0], input_data: getTrainBatch(ids, i)[0],
                                                  y: getTrainBatch(ids, i)[1]})
            # Compute average loss
            avg_cost += c / no_train_data_batch
            # Display logs per epoch step
            if (epoch + 1) % display_step == 0:
                print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))

    print("Optimization Finished!")

    # # Test model
    # correct_prediction = tf.equal(tf.argmax(weighted_pred, 1), tf.argmax(y, 1))
    correct_prediction = tf.equal(tf.argmax(new_prediction, 1), tf.argmax(y, 1))
    # # Calculate accuracy
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    #
    # zip(compressed_test_ids, getTestBatch(ids))

    training_result = []
    for i in tqdm(range(len(test_idslabel))):
        result = sess.run(accuracy, feed_dict={x: test_idslabel[i][0], input_data: getTestBatch(ids, i)[0],
                                               y: getTestBatch(ids, i)[1]})
        # y: test_idslabel[i][1]})
        training_result.append(result)

    final_acc = sum(training_result) / len(training_result)
    print('Final accuracy: %f ' % final_acc)

    # for j in len(test_idslabel):
    #     print("Accuracy:",
    #           accuracy.eval({x: test_idslabel[j][0], input_data: getTestBatch(ids, j)[0], y: test_idslabel[j][1]}))
