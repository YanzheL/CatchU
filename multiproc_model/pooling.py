from multiprocessing import Pool
from threading import Thread, stack_size

from utils.logger_router import LoggerRouter
from utils.singleton import Singleton

logger = LoggerRouter().getLogger(__name__)

class ThreadPool:
    def __init__(self):
        self.logger = LoggerRouter().getLogger(__name__)
        self.workers = {}
        self.started = False
        stack_size(65536)

    def add_worker(self, worker_instance, method='run', args=(), name=None, nworkers=1, daemon=True, kwargs=None):
        func = getattr(worker_instance, method)
        worker_info = self.workers.get(worker_instance.__class__, None)
        nworkers=int(nworkers)
        if worker_info:
            worker_info['nworkers'] += nworkers
            worker_info['threads'].extend(
                ThreadPool._make_threads_list(self, worker_instance, nworkers, target=func, args=args, daemon=daemon,
                                              name=name, kwargs=kwargs)
            )

        else:
            self.workers[worker_instance.__class__] = {
                'nworkers': int(nworkers),
                'threads': ThreadPool._make_threads_list(self, worker_instance, nworkers, target=func, args=args,
                                                         daemon=daemon, name=name, kwargs=kwargs)
            }

    def start(self, all_start=True, worker_cls=None, **kwargs):
        if all_start:
            for worker_class in self.workers:
                self._start_worker_threads(worker_class)
        elif worker_cls:
            self._start_worker_threads(worker_cls)
        self.started = True

    def stop(self, all_stop=True, cls=None):
        if all_stop:
            for worker_class in self.workers:
                self._stop_worker_threads(worker_class)
        elif cls:
            self._stop_worker_threads(cls)
        self.started = False

    # def wait(self):
    #     for k, v in self.workers.items():
    #         logger.info('Now waitting for %s' % str(k.__name__))
    #         k.all_stopped.wait()

    def wait(self, cls):
        logger.info('Now waitting for %s' % str(cls.__name__))
        cls.all_stopped.wait()

    def _make_threads_list(self, worker_instance, nworkers, **thread_params):
        self.logger.info("Made %d threads for worker class %s" % (nworkers, worker_instance.__class__.__name__))
        return [(Thread(**thread_params), worker_instance) for i in range(nworkers)]

    def _start_worker_threads(self, worker_class):
        worker_info = self.workers.get(worker_class, None)
        if worker_info:
            for th in worker_info['threads']:
                th[0].start()
        else:
            self.logger.error('Cannot find specific thread class %s, skipped' % worker_class)

    def _stop_worker_threads(self, worker_class, all_instance=True):
        # worker_class.global_running=False
        worker_info = self.workers.get(worker_class, None)
        if worker_info:
            # logger.info(worker_info['threads'])
            for th in worker_info['threads']:
                # logger.info(th)
                if all_instance:
                    # th[1].global_running=False
                    th[1].stop(all_instance=True)
                    break
                    # TODO: implement stop thread based on worker number rather than stop all
        else:
            self.logger.error('Cannot find specific thread class %s, skipped' % worker_class)


class SingletonProcessPool(metaclass=Singleton):
    def __init__(self, **kwargs):
        self.pool = Pool(**kwargs)

    def apply(self, func, args=(), kwds={}):
        return self.pool.apply(func, args, kwds)

    def close(self):
        self.pool.close()
