import numpy as np
import codecs
# import tensorflow as tf
import sys

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
labels = []
maxSeqLength = 3
fileCounter = 0
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

with codecs.open('../data/datawide-gram' + str(grams) + suffix + '.txt', 'r') as f:
    lines = [x.strip() for x in f.readlines()]

number_of_data = len(lines)
ids = np.zeros([number_of_data, maxSeqLength], dtype='int32')
for line in lines:
    lsplit = line.split(':::')
    if len(lsplit) == 1:
        pass
    else:
        ssplit = lsplit[1].split('\t')
        assert len(ssplit) == 3
        try:
            ids[fileCounter][0] = category.index(ssplit[0])
            ids[fileCounter][1] = btnclass.index(ssplit[1])
            ids[fileCounter][2] = position.index(ssplit[2])
            fileCounter += 1
        except ValueError:
            print(line)

print(ids.shape)
# Parameters
# learning_rate = 0.01
# training_epochs = 25
# batch_size = 100
# display_step = 1
#
# # tf Graph Input
# x = tf.placeholder(tf.float32, [None, 3])  # mnist data image of shape 28*28=784
# y = tf.placeholder(tf.float32, [None, 2])  # 0-9 digits recognition => 10 classes
#
# # Set model weights
# W = tf.Variable(tf.zeros([3, 2]))
# b = tf.Variable(tf.zeros([2]))
#
# # Construct model
# pred = tf.nn.softmax(tf.matmul(x, W) + b)  # Softmax
#
# # Minimize error using cross entropy
# cost = tf.reduce_mean(-tf.reduce_sum(y * tf.log(pred), reduction_indices=1))
# # Gradient Descent
# optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)
#
# # Initialize the variables (i.e. assign their default value)
# init = tf.global_variables_initializer()
#
# # Start training
# with tf.Session() as sess:
# # Run the initializer
#     sess.run(init)
#
# # Training cycle
# for epoch in range(training_epochs):
#     avg_cost = 0.
# total_batch = int(mnist.train.num_examples / batch_size)
# # Loop over all batches
# for i in range(total_batch):
#     batch_xs, batch_ys = mnist.train.next_batch(batch_size)
#     print(batch_xs.shape)
#     print(batch_ys.shape)
#     exit(1)
# # Run optimization op (backprop) and cost op (to get loss value)
#     _, c = sess.run([optimizer, cost], feed_dict={x: batch_xs,
#                                               y: batch_ys})
# # Compute average loss
#     avg_cost += c / total_batch
#     # Display logs per epoch step
#     if (epoch + 1) % display_step == 0:
#         print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))
#
# print("Optimization Finished!")
#
# # Test model
# correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
# # Calculate accuracy
# accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
# print("Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))
