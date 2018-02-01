from gensim.models import Word2Vec
from random import randint

import tensorflow as tf
import numpy as np
import codecs
import datetime
import math

"""Change value"""
grams = 4
treat_as_individual_word = True
"""END Change value"""

if treat_as_individual_word:
    suffix = 'iw'
else:
    suffix = ''

with codecs.open('../data/dataseq-gram' + str(grams) + suffix + '.txt', 'r', 'utf-8') as f:
    lines = [x.strip('\n') for x in f.readlines()]

model = Word2Vec.load('../data/model' + str(grams) + suffix + '.bin')
wordList = np.load('../data/wordList' + str(grams) + suffix + '.npy')
wordList = wordList.tolist()
wordVector = np.load('../data/wordVector' + str(grams) + suffix + '.npy')
labellist = []
sequencelist = []


def populate_seqlab():
    for i in range(len(lines)):
        lsplit = lines[i].split(':::')
        if len(lsplit) == 2:
            labellist.append(lsplit[0])
            sequencelist.append(lsplit[1])
        else:
            sequencelist[-1] += '\n' + lines[i]

    print(len(labellist))
    print(len(sequencelist))
    return len(labellist)


def convert_to_ids():
    """ Converting of text into ids """
    wordCount = []
    for i in sequencelist:
        wordCount.append(len(i.split('\t')))
    maxLength = math.ceil(sum(wordCount) / len(wordCount))
    ids = np.zeros((number_of_data, maxLength), dtype='int32')
    fileCounter = 0
    for i in sequencelist:
        lsplit = i.split('\t')
        indexCounter = 0
        for section in lsplit:
            try:
                ids[fileCounter][indexCounter] = wordList.index(section)
            except Exception:
                print(section)
            indexCounter += 1
            if indexCounter >= maxLength:
                break
        fileCounter += 1

    print(ids)
    np.save('../data/idsMatrix' + str(grams) + suffix, ids)


""" Start of RNN """

""" Perimeters """
batchSize = 24
lstmUnits = 64
numClasses = 2
iterations = 100000
maxSeqLength = grams + 1
numDimensions = 50
""" End Perimeters """


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


def getTestBatch(ids):
    labels = []
    arr = np.zeros([batchSize, maxSeqLength])
    i = 0
    while i < batchSize:
        num = randint(int(9 / 10 * number_of_data), number_of_data)
        if labellist[num] == 'positive':
            labels.append([1, 0])
        elif labellist[num] == 'negative':
            labels.append([0, 1])
        else:
            continue
        arr[i] = ids[num - 1: num]
        i += 1
    return arr, labels


def learn():
    ids = np.load('../data/idsMatrix' + str(grams) + suffix + '.npy')

    tf.reset_default_graph()

    labels = tf.placeholder(tf.float32, [batchSize, numClasses])
    input_data = tf.placeholder(tf.int32, [batchSize, maxSeqLength])

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

    for i in range(iterations):
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


number_of_data = populate_seqlab()
# convert_to_ids()
learn()
