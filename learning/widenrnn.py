import numpy as np
import codecs
import tensorflow as tf

category = {
    'tools', 'game_simulation', 'game_word', 'personalization', 'media_and_video', 'shopping',
    'game_role_playing', 'productivity', 'game_educational', 'game_action', 'social', 'news_and_magazines',
    'game_arcade', 'game_casino', 'health_and_fitness', 'lifestyle', 'photography', 'game_strategy',
    'communication', 'game_adventure', 'game_card', 'game_board', 'transportation', 'game_music', 'business',
    'game_casual', 'sports', 'game_racing', 'finance', 'travel_and_local', 'music_and_audio',
    'libraries_and_demo', 'weather', 'books_and_reference', 'entertainment', 'education', 'game_puzzle',
    'game_trivia', 'medical', 'comics', 'game_sports'}
btnclass = {
    'EditText', 'RadioButton', 'CheckedTextView', 'CompoundButton', 'ImageView', 'TextInputLayout', 'Button',
    'MultiAutoCompleteTextView', 'ToggleButton', 'CheckBox', 'TextView', 'RelativeLayout', 'View',
    'DigitalClock', 'Switch'}
position = {'-1', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

batch_size = 24

with codecs.open('../data/wnd-train.txt', 'r') as f:
    lines = [x.strip() for x in f.readlines()]

data = []
labels = []
np.zeros([batch_size, 3], dtype='int32')
for line in lines:
    lsplit = line.split(',')
    print(lsplit)

    break

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
