import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict


class Objects:
    def __init__(self, max_disappeared=6, start_id=0, initial_count=0):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = start_id
        self.objects = OrderedDict()
        self.radii = OrderedDict()
        self.disappeared = OrderedDict()
        self.count = initial_count

        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.max_disappeared = max_disappeared

    def register(self, centroid, radius):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objects[self.nextObjectID] = centroid
        self.radii[self.nextObjectID] = radius
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, object_id):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[object_id]
        del self.radii[object_id]
        del self.disappeared[object_id]
        # the "count" is +=1 when the object is deregistered longer than 5 frames
        self.count += 1

    def update(self, rectangles, radii):
        # check to see if the list of input bounding box rectangles
        # is empty
        if len(rectangles) == 0:
            disappeared_keys = list(self.disappeared.keys())
            for object_id in disappeared_keys:
                self.disappeared[object_id] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            # return early as there are no centroids or tracking info
            # to update
            return self.objects, self.radii, self.count

        input_centroids = np.zeros((len(rectangles), 2), dtype="int")
        # 		print(input_centroids.shape)
        input_radii = np.zeros((len(rectangles), 1), dtype="int")

        # loop over the bounding box rectangles
        for (i, (startX, startY, endX, endY)) in enumerate(rectangles):
            # use the bounding box coordinates to derive the centroid
            centroid_x = int((startX + endX) / 2.0)
            centroid_y = int((startY + endY) / 2.0)
            input_centroids[i] = (centroid_x, centroid_y)
        # loop over radii of balls
        for (i, rad) in enumerate(radii):
            input_radii[i] = rad

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i], input_radii[i])
        else:
            # grab the set of object IDs and corresponding centroids
            objects_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            # 			objectRadii = list(self.radii.values())

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            c_distance = dist.cdist(np.array(object_centroids), input_centroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value is at the *front* of the index
            # list
            rows = c_distance.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = c_distance.argmin(axis=1)[rows]
            used_rows = set()
            used_cols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in used_rows or col in used_cols:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                object_id = objects_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.radii[object_id] = input_radii[col]
                self.disappeared[object_id] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                used_rows.add(row)
                used_cols.add(col)
            unused_rows = set(range(0, c_distance.shape[0])).difference(used_rows)
            unused_cols = set(range(0, c_distance.shape[1])).difference(used_cols)
            if c_distance.shape[0] >= c_distance.shape[1]:
                # loop over the unused row indexes
                for row in unused_rows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    object_id = objects_ids[row]
                    self.disappeared[object_id] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants de-registering the object
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_centroids[col], input_radii[col])

        return self.objects, self.radii, self.count
