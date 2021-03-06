# 定义预测过程
import time
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

import mnist_inference
import mnist_train

# 每10s加载一次最新的模型，并在测试数据上测试最新模型的正确性
EVAL_INTERVAL_SEC = 10

def evaluate(mnist):
    with tf.Graph().as_default() as g:
        # 定义输入输出的格式
        x = tf.placeholder(tf.float32, [None, mnist_inference.INPUT_NODE], name='x-input')
        y_ = tf.placeholder(tf.float32, [None, mnist_inference.OUTPUT_NODE], name='y-output')
        validate_feed = {x: mnist.validation.images, y_: mnist.validation.labels}

        # 直接用封装好的函数计算前向传播的结果，因为测试时不关注正则化损失的值，所以为None
        y = mnist_inference.inference(x, None)

        correct_prediction = tf.equal(tf.arg_max(y, 1), tf.arg_max(y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        variable_averages = tf.train.ExponentialMovingAverage(
            mnist_train.MOVING_AVERAGE_DECAY
        )
        variables_to_restore = variable_averages.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)

        while True:
            with tf.Session() as sess:
                ckpt = tf.train.get_checkpoint_state(mnist_train.MODEL_SAVE_PATH)
                if ckpt and ckpt.model_checkpoint_path:
                    # 加载模型
                    saver.restore(sess, ckpt.model_checkpoint_path)
                    global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    accuracy_score = sess.run(accuracy, feed_dict=validate_feed)
                    print("After %s training step(s), validation "
                          "accuracy = %g" % (global_step, accuracy_score))
                else:
                    print('No checkpoint file found!')
                    return
            time.sleep(EVAL_INTERVAL_SEC)


def main(argv=None):
    mnist = input_data.read_data_sets("../../MNIST_DATA", one_hot=True)
    evaluate(mnist)


if __name__ == '__main__':
    tf.app.run()