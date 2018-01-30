from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import pickle
import sys

import numpy as np
import tensorflow as tf
from sklearn.svm import SVC

from third_party.facenet.src import facenet
from third_party.facenet.src.models.inception_resnet_v1 import inference

SESSION_CONF = {
    'config': tf.ConfigProto(
        gpu_options=tf.GPUOptions(
            per_process_gpu_memory_fraction=0.7
        ),
        log_device_placement=0,
        allow_soft_placement=1
    )
}


def main(data_dir, chip_size,batch_size,image_size,classifier_filename):
    with tf.Graph().as_default():
        with tf.Session(**SESSION_CONF) as sess:
            np.random.seed()
            dataset = facenet.get_dataset(data_dir)
            paths, labels = facenet.get_image_paths_and_labels(dataset)

            images_placeholder = tf.placeholder(tf.float32, shape=(None, chip_size, chip_size, 3), name='input')
            phase_train_placeholder = tf.placeholder(tf.bool, name='phase_train')
            embeddings = inference(images_placeholder, 1.0,
                                   phase_train=phase_train_placeholder)[0][0]
            sess.run(tf.global_variables_initializer())

            embedding_size = embeddings.get_shape()[1]

            # Run forward pass to calculate embeddings
            print('Calculating features for images')
            nrof_images = len(paths)
            nrof_batches_per_epoch = int(math.ceil(1.0 * nrof_images / batch_size))
            emb_array = np.zeros((nrof_images, embedding_size))
            for i in range(nrof_batches_per_epoch):
                start_index = i * batch_size
                end_index = min((i + 1) * batch_size, nrof_images)
                paths_batch = paths[start_index:end_index]
                images = facenet.load_data(paths_batch, False, False, image_size)
                feed_dict = {images_placeholder: images, phase_train_placeholder: False}
                emb_array[start_index:end_index, :] = sess.run(embeddings, feed_dict=feed_dict)

            classifier_filename_exp = os.path.expanduser(classifier_filename)

            # Train classifier
            print('Training classifier')
            model = SVC(kernel='rbf', probability=True)
            model.fit(emb_array, labels)

            # Create a list of class names
            class_names = [cls.name.replace('_', ' ') for cls in dataset]

            # Saving classifier model
            with open(classifier_filename_exp, 'wb') as outfile:
                pickle.dump((model, class_names), outfile)
            print('Saved classifier model to file "%s"' % classifier_filename_exp)

if __name__ == '__main__':
    main(sys.argv[2],160,int(sys.argv[1]),160,sys.argv[2])
