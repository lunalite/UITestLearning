import codecs
import datetime
import sys
from random import randint

import numpy as np
from gensim.models import Word2Vec
from tqdm import *


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


def convert_to_ids():
    """ Converting of text into ids """
    print('\nConverting wordList to ids...')
    wordCount = []
    for i in sequencelist:
        wordCount.append(len(i.split('\t')))
    ids = np.zeros((number_of_data, maxSeqLength), dtype='int32')
    fileCounter = 0
    for i in tqdm(sequencelist):
        lsplit = i.split('\t')
        indexCounter = 0
        for section in lsplit:
            try:
                ids[fileCounter][indexCounter] = wordList.index(section)
            except Exception:
                print(section)
            indexCounter += 1
            if indexCounter >= maxSeqLength:
                break
        fileCounter += 1

    print(ids)
    np.save(idsMatrixFile, ids)
    print('\nConversion done. Saved to %s' % idsMatrixFile)


def getTrainBatch(ids):
    labels = []
    arr = np.zeros([batchSize, maxSeqLength])
    i = 0
    while i < batchSize:
        num = randint(1, int(9 / 10 * number_of_data))
        if labellist[num] == 'positive':
            labels.append([1, 0])
        elif labellist[num] == 'negative':
            labels.append([0, 1])
        else:
            continue
        arr[i] = ids[num - 1:num]
        i += 1
    return arr, labels


def getTestBatch(ids, _i):
    labels = []
    arr = np.zeros([batchSize, maxSeqLength])
    i = 0
    # while i < batchSize:
    #     num = randint(int(9 / 10 * number_of_data), number_of_data)
    #     if labellist[num] == 'positive':
    #         labels.append([1, 0])
    #     elif labellist[num] == 'negative':
    #         labels.append([0, 1])
    #     else:
    #         continue
    #     arr[i] = ids[num - 1: num]
    #     i += 1
    num = int(9 / 10 * number_of_data) + _i * batchSize
    try:
        while i < batchSize:
            if labellist[num] == 'positive':
                labels.append([1, 0])
            elif labellist[num] == 'negative':
                labels.append([0, 1])
            else:
                num += 1
                continue
            arr[i] = ids[num - 1: num]
            i += 1
            num += 1
        return arr, labels
    except IndexError:
        return None, None


def learn():
    print('\nLearning...')
    print('Loading from %s' % idsMatrixFile)
    ids = np.load(idsMatrixFile)

    tf.reset_default_graph()

    labels = tf.placeholder(tf.float32, [None, numClasses])
    input_data = tf.placeholder(tf.int32, [None, maxSeqLength])

    data = tf.Variable(tf.zeros([batchSize, maxSeqLength, numDimensions]), dtype=tf.float32)
    data = tf.nn.embedding_lookup(wordVector, input_data)

    lstmCell = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
    lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=0.75)
    value, _ = tf.nn.dynamic_rnn(lstmCell, data, dtype=tf.float32)

    weight = tf.Variable(tf.truncated_normal([lstmUnits, numClasses]))
    bias = tf.Variable(tf.constant(0.1, shape=[numClasses]))
    value = tf.transpose(value, [1, 0, 2])
    last = tf.gather(value, int(value.get_shape()[0]) - 1)
    prediction = (tf.matmul(last, weight) + bias)

    correctPred = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correctPred, tf.float32))

    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=labels))
    optimizer = tf.train.AdamOptimizer().minimize(loss)

    sess = tf.InteractiveSession()
    saver = tf.train.Saver()
    sess.run(tf.global_variables_initializer())

    tf.summary.scalar('Loss', loss)
    tf.summary.scalar('Accuracy', accuracy)
    merged = tf.summary.merge_all()
    logdir = "tensorboard/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "/"
    writer = tf.summary.FileWriter(logdir, sess.graph)

    for i in tqdm(range(iterations)):
        # Next Batch of reviews
        nextBatch, nextBatchLabels = getTrainBatch(ids)
        sess.run(optimizer, {input_data: nextBatch, labels: nextBatchLabels})

        # Write summary to Tensorboard
        if i % 50 == 0:
            summary = sess.run(merged, {input_data: nextBatch, labels: nextBatchLabels})
            writer.add_summary(summary, i)

        # Save the network every 10,000 training iterations
        if i % 10000 == 0 and i != 0:
            save_path = saver.save(sess, "models/pretrained_lstm.ckpt", global_step=i)
            print("saved to %s" % save_path)
    writer.close()


def test():
    print('\nTesting....')
    print('Loading from %s' % idsMatrixFile)
    ids = np.load(idsMatrixFile)

    labels = tf.placeholder(tf.float32, [None, numClasses])
    input_data = tf.placeholder(tf.int32, [None, maxSeqLength])

    data = tf.Variable(tf.zeros([batchSize, maxSeqLength, numDimensions]), dtype=tf.float32)
    data = tf.nn.embedding_lookup(wordVector, input_data)

    lstmCell = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
    lstmCell = tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=0.75)
    value, _ = tf.nn.dynamic_rnn(lstmCell, data, dtype=tf.float32)

    weight = tf.Variable(tf.truncated_normal([lstmUnits, numClasses]))
    bias = tf.Variable(tf.constant(0.1, shape=[numClasses]))
    value = tf.transpose(value, [1, 0, 2])
    last = tf.gather(value, int(value.get_shape()[0]) - 1)
    prediction = (tf.matmul(last, weight) + bias)

    correctPred = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correctPred, tf.float32))

    sess = tf.InteractiveSession()
    saver = tf.train.Saver()
    saver.restore(sess, tf.train.latest_checkpoint('models'))

    training_result = []
    for i in tqdm(range(int(notestdata / batchSize))):
        nextBatch, nextBatchLabels = getTestBatch(ids, i)
        if nextBatch is None and nextBatchLabels is None:
            break
        result = sess.run(accuracy, feed_dict={input_data: nextBatch, labels: nextBatchLabels})
        training_result.append(result)

    final_acc = sum(training_result) / len(training_result)
    print('Final accuracy: %f ' % final_acc)

    with open('./testresult.txt', 'a') as f:
        f.write('%d-grams with iw = %s: %f\n' % (grams, treat_as_individual_word, final_acc))


try:
    if len(sys.argv) < 4:
        raise IndexError

    import tensorflow as tf

    treat_as_individual_word = False
    suffix = ''

    grams = int(sys.argv[1])
    if sys.argv[2] == '1':
        treat_as_individual_word = True
        suffix = 'iw'
    elif sys.argv[2] == '11':
        suffix = 'iwin'
        treat_as_individual_word = True
        treat_all_null_as_invalid = True
    elif sys.argv[2] == '01':
        suffix = 'in'
        treat_all_null_as_invalid = True

    maxSeqLength = grams * 3

    with codecs.open('../data/dataseq-gram' + str(grams) + suffix + '.txt', 'r', 'utf-8') as f:
        lines = [x.strip('\n') for x in f.readlines()]

    model = Word2Vec.load('../data/model' + str(grams) + suffix + '.bin')
    wordList = np.load('../data/wordList' + str(grams) + suffix + '.npy')
    wordList = wordList.tolist()
    wordVector = np.load('../data/wordVector' + str(grams) + suffix + '.npy')
    labellist = []
    sequencelist = []
    idsMatrixFile = '../data/idsMatrix' + str(grams) + suffix + '.npy'

    """ Parameters """
    batchSize = 24
    lstmUnits = 64
    numClasses = 2
    iterations = 100000
    numDimensions = 50
    """ End Parameters """

    number_of_data = populate_seqlab()
    notestdata = number_of_data - int(9 / 10 * number_of_data)

    print(int(notestdata))
    if 'c' in sys.argv[3]:
        convert_to_ids()
    if 'l' in sys.argv[3]:
        learn()
    elif 't' in sys.argv[3]:
        test()
except IndexError:
    print('Please enter arguments:')
    print('argv[1] == n: n-gram.')
    print('argv[2] == 1/0: Treating individual word or not.')
    print('argv[2] == 1/0: Treating individual word or not.')
    print('argv[2] == 11/01: Treat all null sequence as invalid.')
    print('argv[3] == c: convert to ids')
    print('argv[3] == l: learn')
    print('argv[3] == t: test')
