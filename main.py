# coding: utf-8
import traceback
from queue import Queue, PriorityQueue

from backend.face_detectors import *
from multiproc_model.pooling import ThreadPool
from multiproc_model.producer import Producer
from multiproc_model.worker import Worker
from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger("main")
import cv2


def main():
    datasource_queue = Queue(WORKER_CONF['input_que_size'])
    data_out_queue = PriorityQueue(WORKER_CONF['output_que_size'])
    thread_pool = None
    try:
        main_producer = Producer.from_name("video", output_queue=datasource_queue)
        worker_base = Worker.from_name("video", input_queue=datasource_queue, output_queue=data_out_queue,
                                       use_multiprocess=False)

        thread_pool = ThreadPool()
        thread_pool.add_worker(main_producer, name='main_producer')
        thread_pool.add_worker(worker_base, nworkers=WORKER_CONF['workers'])

        thread_pool.start()
        lens = 0
        while True:
            out_data = data_out_queue.get()
            size = data_out_queue.qsize()
            # logger.info(
            #     "seq = %d, in size = %d, out size = %d, diff = %d" % (
            #         out_data[0], datasource_queue.qsize(), size, size - lens
            #     )
            # )
            lens = size
            cv2.imshow("preview", out_data[1])
            # cv2.imwrite('get_best_class/' + str(out_data[0]) + '.jpg', out_data[1])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error("Uncaught exception '%s' traceback as follows:" % str(e))
        traceback.print_exc()
        os.error(1)
    finally:
        thread_pool.stop()
        # logger.info("App closing...")
        print("App closing...")
        thread_pool.wait()
        # logger.info("Bye bye!")
        print("Bye bye!")


if __name__ == '__main__':
    main()
    # imgtest()
