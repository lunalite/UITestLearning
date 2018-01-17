import shutil
import sys
import tensorflow as tf

_CSV_COLUMNS = [
    'category', 'btn_class', 'label'
]

_CSV_COLUMN_DEFAULTS = [[''], [''], ['']]


def build_model_columns():
    """Builds a set of wide and deep feature columns."""

    category = tf.feature_column.categorical_column_with_vocabulary_list(
        'category', [
            'finance', 'game_board', 'productivity', 'game_racing', 'game_puzzle', 'social', 'comics', 'tools',
            'game_sports', 'game_casino', 'game_action', 'entertainment', 'music_and_audio', 'weather',
            'books_and_reference', 'business', 'game_trivia', 'game_simulation', 'game_casual', 'game_educational',
            'game_arcade', 'lifestyle', 'game_role_playing', 'game_word', 'sports', 'medical', 'game_strategy',
            'education', 'news_and_magazines', 'media_and_video', 'shopping', 'transportation', 'travel_and_local',
            'libraries_and_demo', 'health_and_fitness', 'game_music', 'photography', 'game_card', 'game_adventure',
            'personalization', 'communication'])

    btn_class = tf.feature_column.categorical_column_with_vocabulary_list(
        'btn_class', [
            'checkbox', 'textview', 'checkedtextview', 'togglebutton', 'relativelayout', 'radiobutton',
            'multiautocompletetextview', 'compoundbutton', 'digitalclock', 'imageview', 'edittext', 'textinputlayout',
            'switch', 'button'])

    # Wide columns and deep columns.
    base_columns = [
        category, btn_class
    ]

    wide_columns = base_columns

    return wide_columns, None


def build_estimator(model_dir, model_type):
    """Build an estimator appropriate for the given model type."""
    wide_columns, deep_columns = build_model_columns()
    hidden_units = [100, 75, 50, 25]

    # Create a tf.estimator.RunConfig to ensure the model is run on CPU, which
    # trains faster than GPU for this model.
    run_config = tf.estimator.RunConfig().replace(
        session_config=tf.ConfigProto(device_count={'GPU': 0}))

    if model_type == 'wide':
        return tf.estimator.LinearClassifier(
            model_dir=model_dir,
            feature_columns=wide_columns,
            config=run_config)
    elif model_type == 'deep':
        return tf.estimator.DNNClassifier(
            model_dir=model_dir,
            feature_columns=deep_columns,
            hidden_units=hidden_units,
            config=run_config)
    else:
        return tf.estimator.DNNLinearCombinedClassifier(
            model_dir=model_dir,
            linear_feature_columns=wide_columns,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=hidden_units,
            config=run_config)


def get_input(data_file, num_epochs, batch_size):
    def parse_csv(value):
        columns = tf.decode_csv(value, record_defaults=_CSV_COLUMN_DEFAULTS)
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('label')
        return features, tf.equal(labels, 'positive')

    dataset = tf.data.TextLineDataset(data_file)
    dataset = dataset.map(parse_csv, num_parallel_calls=5)
    dataset = dataset.repeat(num_epochs)
    dataset = dataset.batch(batch_size)
    iterator = dataset.make_one_shot_iterator()
    features, labels = iterator.get_next()
    return features, labels


# def main(unused_argv):
#     model = build_estimator(FLAGS.model_dir, FLAGS.model_type)
#
#     # Train and evaluate the model every `FLAGS.epochs_per_eval` epochs.
#     for n in range(FLAGS.train_epochs // FLAGS.epochs_per_eval):
#         model.train(input_fn=lambda: input_fn(
#             FLAGS.train_data, FLAGS.epochs_per_eval, True, FLAGS.batch_size))
#
#         results = model.evaluate(input_fn=lambda: input_fn(
#             FLAGS.test_data, 1, False, FLAGS.batch_size))
#
#         # Display evaluation metrics
#         print('Results at epoch', (n + 1) * FLAGS.epochs_per_eval)
#         print('-' * 60)
#
#         for key in sorted(results):
#             print('%s: %s' % (key, results[key]))


if __name__ == '__main__':
    get_input('../dataparsing/wnd-train.txt', 10, 40)
    # tf.logging.set_verbosity(tf.logging.INFO)
    # FLAGS, unparsed = parser.parse_known_args()
    # tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
