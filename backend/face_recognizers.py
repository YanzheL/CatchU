# coding: utf-8

import os
import sys
import time
from threading import Event

import cv2
import numpy as np
import tensorflow as tf
from sklearn.externals import joblib

from settings import SESSION_CONF
from third_party.facenet.src.models.inception_resnet_v1 import inference
from utils.config import Configure
from utils.logger_router import LoggerRouter
from utils.singleton import Singleton
import pickle
from third_party.facenet.src import facenet

RECOGNIZER_CONF = Configure().deserialize('recognizer')

logger = LoggerRouter().getLogger(__name__)


# i=1500

class FaceRecognitor(metaclass=Singleton):
    initializing = Event()
    initialized = Event()

    def __init__(self):
        logger.info('Preloading facenet embedding model in background...')
        self.initializing.set()
        self.chip_size = RECOGNIZER_CONF.getint('chip_size')

        with open(os.path.join(sys.path[0], RECOGNIZER_CONF['classifier']), 'rb') as infile:
            self.model, self.class_names = pickle.load(infile)
        logger.info('Loaded classifier model from file "%s"' % os.path.join(sys.path[0], RECOGNIZER_CONF['classifier']))

        logger.info('Now generating embeding network...')
        t1 = time.time()
        with tf.Graph().as_default():
            self.images_placeholder = tf.placeholder(tf.float32, shape=(None, self.chip_size, self.chip_size, 3),
                                                     name='input')
            self.phase_train_placeholder = tf.placeholder(tf.bool, name='phase_train')

            # facenet.load_model(RECOGNIZER_CONF['model_folder'])

            # Get input and output tensors
            # self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            # self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            # self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
            # self.embedding_size = self.embeddings.get_shape()[1]
            self.embeddings = inference(self.images_placeholder, 1.0,
                                        phase_train=self.phase_train_placeholder)
            self.sess = tf.Session(**SESSION_CONF)
            with self.sess.as_default():
                self.sess.run(tf.global_variables_initializer())

        logger.info("Preloaded facenet embedding network, time used = %f ms" % ((time.time() - t1) * 1000))

        self.runtime_sess = self.sess.as_default()

        self.initialized.set()

    def get_best_class(self, emb_array):
        t1 = time.time()
        predictions = self.model.predict_proba(emb_array)
        t2 = time.time()
        best_class_indices = np.argmax(predictions, axis=1)
        logger.info("Predictions = %s, best_class_indices = %s, time used = %f ms" % (
            predictions, best_class_indices, (t2 - t1) * 1000))
        # best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
        #
        # for i in range(len(best_class_indices)):
        #     logger.info('%4d  %s: %.3f' % (i, self.class_names[best_class_indices[i]], best_class_probabilities[i]))

        # accuracy = np.mean(np.equal(best_class_indices, labels))
        # logger.info('Accuracy: %.3f' % accuracy)
        return best_class_indices

    def get_embedding_metrics(self, batch):
        self.initialized.wait()
        if len(batch):
            t1 = time.time()
            emb_data = self.sess.run(
                [self.embeddings],
                feed_dict={self.images_placeholder: batch, self.phase_train_placeholder: False}
            )[0][0]
            # with self.sess.as_default():
            #     emb_data = self.sess.run([self.embeddings], feed_dict={self.images_placeholder: batch,
            #                                                            self.phase_train_placeholder: False})[0][0]
            t2 = time.time()
            logger.info("EMB calculation time = %f ms" % ((t2 - t1) * 1000))
            return emb_data

    def predict(self, chips):
        self.initialized.wait()
        filtered = np.array(
            [cv2.resize(chip, (self.chip_size, self.chip_size), interpolation=cv2.INTER_CUBIC) for chip in chips if
             chip.size])
        if len(filtered):
            emb_data = self.get_embedding_metrics(filtered)
            return self.get_best_class(emb_data)
        else:
            return []























            # class FaceRecognitor(metaclass=Singleton):
            #     initializing = Event()
            #     initialized = Event()
            #
            #     def __init__(self):
            #         logger.info('Preloading facenet embedding model in background...')
            #         self.initializing.set()
            #         t1 = time.time()
            #         self.chip_size = RECOGNIZER_CONF.getint('chip_size')
            #         self.model = joblib.load(os.path.join(sys.path[0], RECOGNIZER_CONF['classifier']))
            #         with tf.Graph().as_default():
            #             self.images_placeholder = tf.placeholder(tf.float32, shape=(None, self.chip_size, self.chip_size, 3),
            #                                                      name='input')
            #             self.phase_train_placeholder = tf.placeholder(tf.bool, name='phase_train')
            #             self.embeddings = inference(self.images_placeholder, 1.0,
            #                                         phase_train=self.phase_train_placeholder)
            #             self.sess = tf.Session(**SESSION_CONF)
            #             with self.sess.as_default():
            #                 self.sess.run(tf.global_variables_initializer())
            #
            #         logger.info("Preloaded facenet embedding model, time used = %f ms" % ((time.time() - t1) * 1000))
            #         self.initialized.set()
            #
            #     def get_embedding_metrics(self, batch):
            #         self.initialized.wait()
            #         if len(batch):
            #             with self.sess.as_default():
            #                 emb_data = self.sess.run([self.embeddings], feed_dict={self.images_placeholder: batch,
            #                                                                        self.phase_train_placeholder: False})[0][0]
            #             logger.info(emb_data)
            #             return emb_data
            #
            #     def predict(self, frame, chips):
            #         self.initialized.wait()
            #         # global i
            #         filtered = np.array(
            #             [cv2.resize(chip, (self.chip_size, self.chip_size), interpolation=cv2.INTER_CUBIC) for chip in chips if
            #              chip.size])
            #         if len(filtered):
            # for c in chips:
            #     cv2.imwrite("test_files/chip%d.png"%i,c)
            #     i+=1
            # emb_data = self.get_embedding_metrics(filtered)
            # predict = self.model.predict(emb_data)
            # logger.info(predict)



            # logger.info(emb_data)
            # for chip in chips:
            # print(len(chip))
            #     chip = cv2.resize(chip, (96, 96), interpolation=cv2.INTER_CUBIC)
            #     cv2.imwrite("test_files/c%d.png" % random.randint(1, 100), chip)
            #
            #     # data = chip.reshape(-1, 96, 96, 3)
            #     data = chip
            # cv2.imwrite(str(rd.randint(0,100)) + ".jpg", data)

            #
            # predict = self.model.predict(emb_data)
            #
            # if predict == 1:
            #     find_results.append('me')
            # elif predict == 2:
            #     find_results.append('others')

            # cv2.putText(frame, 'detected:{}'.format(find_results), (5, 10),
            #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 0, 0),
            #             thickness=2, lineType=2)
