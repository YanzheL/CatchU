from queue import PriorityQueue


class Pipeline(PriorityQueue):
    def _init(self, maxsize):
        super()._init(maxsize)
        self.stopped = False

    def stop(self):
        self.stopped = True

    def get(self, **kwargs):
        if self.stopped:
            raise BrokenPipeError("Pipeline stopped")
        return super().get(**kwargs)

    def put(self, item, **kwargs):
        if self.stopped:
            raise BrokenPipeError("Pipeline stopped")
        super().put(item, **kwargs)
