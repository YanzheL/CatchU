# class PriorityQueue:
#     def __init__(self, buf=0):
#         self._queue = []
#         self._index = 0
#         self._cv = Condition()
#         self.buf = buf
#
#     def put(self, item, priority):
#         with self._cv:
#             # self._queue.append(item)
#             heapq.heappush(self._queue, (priority, self._index, item))
#             self._index += 1
#             self._cv.notify()
#             # logging.error(len(self._queue))
#
#     def get(self):
#         with self._cv:
#             while len(self._queue) == 0:
#                 # print("waitting..")
#                 self._cv.wait()
#             # return self._queue[-1]
#             return heapq.heappop(self._queue)[-1]
#
#
#     def size(self):
#         return len(self._queue)