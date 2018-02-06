import argparse
import shutil
import sys

import tensorflow as tf

_CSV_COLUMNS = [
    'category', 'btnclass', 'position', 'exploration'
]

_CSV_COLUMN_DEFAULTS = [[''], ['-1'], [''], ['']]

parser = argparse.ArgumentParser()

parser.add_argument(
    '--model_dir', type=str, default='../data/widedata/',
    help='Base directory for the model.')

parser.add_argument(
    '--train_epochs', type=int, default=40, help='Number of training epochs.')

parser.add_argument(
    '--epochs_per_eval', type=int, default=2,
    help='The number of training epochs to run between evaluations.')

parser.add_argument(
    '--batch_size', type=int, default=40, help='Number of examples per batch.')

parser.add_argument(
    '--train_data', type=str, default='../data/wnd-train.txt',
    help='Path to the training data.')

parser.add_argument(
    '--test_data', type=str, default='../data/wnd-test.txt',
    help='Path to the test data.')

_NUM_EXAMPLES = {
    'train': 125914,
    'validation': 13992,
}


def build_model_columns():
    """Builds a set of wide and deep feature columns."""

    category = tf.feature_column.categorical_column_with_vocabulary_list(
        'category', [
            'tools', 'game_simulation', 'game_word', 'personalization', 'media_and_video', 'shopping',
            'game_role_playing', 'productivity', 'game_educational', 'game_action', 'social', 'news_and_magazines',
            'game_arcade', 'game_casino', 'health_and_fitness', 'lifestyle', 'photography', 'game_strategy',
            'communication', 'game_adventure', 'game_card', 'game_board', 'transportation', 'game_music', 'business',
            'game_casual', 'sports', 'game_racing', 'finance', 'travel_and_local', 'music_and_audio',
            'libraries_and_demo', 'weather', 'books_and_reference', 'entertainment', 'education', 'game_puzzle',
            'game_trivia', 'medical', 'comics', 'game_sports'])

    btnclass = tf.feature_column.categorical_column_with_vocabulary_list(
        'btnclass', [
            'EditText', 'RadioButton', 'CheckedTextView', 'CompoundButton', 'ImageView', 'TextInputLayout', 'Button',
            'MultiAutoCompleteTextView', 'ToggleButton', 'CheckBox', 'TextView', 'RelativeLayout', 'View',
            'DigitalClock', 'Switch'])

    position = tf.feature_column.categorical_column_with_vocabulary_list(
        'position', [
            '-1', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    # Wide columns and deep columns.
    base_columns = [
        category, btnclass, position, ]

    # crossed_columns = [
    #     tf.feature_column.crossed_column(
    #         ['education', 'occupation'], hash_bucket_size=1000),
    #     tf.feature_column.crossed_column(
    #         [age_buckets, 'education', 'occupation'], hash_bucket_size=1000),
    # ]

    # wide_columns = base_columns + crossed_columns
    wide_columns = base_columns

    return wide_columns, None


def build_estimator(model_dir):
    """Build an estimator appropriate for the given model type."""
    wide_columns, deep_columns = build_model_columns()
    hidden_units = [100, 75, 50, 25]

    # Create a tf.estimator.RunConfig to ensure the model is run on CPU, which
    # trains faster than GPU for this model.
    run_config = tf.estimator.RunConfig().replace(
        session_config=tf.ConfigProto(device_count={'GPU': 0}))

    return tf.estimator.LinearClassifier(
        model_dir=model_dir,
        feature_columns=wide_columns,
        config=run_config)


def input_fn(data_file, num_epochs, shuffle, batch_size):
    """Generate an input function for the Estimator."""
    assert tf.gfile.Exists(data_file), (
            '%s not found. Please make sure you have either run data_download.py or '
            'set both arguments --train_data and --test_data.' % data_file)

    def parse_csv(value):
        print('Parsing', data_file)
        columns = tf.decode_csv(value, record_defaults=_CSV_COLUMN_DEFAULTS)
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('exploration')
        return features, tf.equal(labels, 'positive')

    # Extract lines from input files using the Dataset API.
    dataset = tf.data.TextLineDataset(data_file)

    if shuffle:
        dataset = dataset.shuffle(buffer_size=_NUM_EXAMPLES['train'])

    dataset = dataset.map(parse_csv, num_parallel_calls=5)

    # We call repeat after shuffling, rather than before, to prevent separate
    # epochs from blending together.
    dataset = dataset.repeat(num_epochs)
    dataset = dataset.batch(batch_size)

    iterator = dataset.make_one_shot_iterator()
    features, labels = iterator.get_next()
    return features, labels


def main(unused_argv):
    # Clean up the model directory if present
    shutil.rmtree(FLAGS.model_dir, ignore_errors=True)
    model = build_estimator(FLAGS.model_dir)

    # Train and evaluate the model every `FLAGS.epochs_per_eval` epochs.
    for n in range(FLAGS.train_epochs // FLAGS.epochs_per_eval):
        model.train(input_fn=lambda: input_fn(
            FLAGS.train_data, FLAGS.epochs_per_eval, True, FLAGS.batch_size))

        results = model.evaluate(input_fn=lambda: input_fn(
            FLAGS.test_data, 1, False, FLAGS.batch_size))

        # Display evaluation metrics
        print('Results at epoch', (n + 1) * FLAGS.epochs_per_eval)
        print('-' * 60)

        for key in sorted(results):
            print('%s: %s' % (key, results[key]))


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
