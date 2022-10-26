import os
import time
from datetime import datetime
import cv2
import numpy
from modbus_tk import modbus_tcp, defines as cst
from roboflowoak import RoboflowOak
from scipy.spatial import distance
from collections import OrderedDict

DATA = 0
FRAME = 1


class FileManager:

    def __init__(self, filepath, filename):
        self.filepath = filepath
        self.filename = filename

    def get_int(self, default=0):
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        with open("{}/{}".format(self.filepath, self.filename)) as file:
            lines = file.read()
            first = lines.split('\n', 1)[0]
        if first == "":
            return default
        return int(first)

    def set_int(self, value):
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        file = open("{}/{}".format(self.filepath, self.filename), 'w')
        current = self.get_int()
        while current != value:
            file.write(str(value))
            current = self.get_int()
        file.close()

    def reset(self):
        self.set_int(0)


class MemoryMapper:
    equip_stat = 1  # EquipStat     (int)
    lb_count = 0  # LbCount       (int)   Number of objects recognized
    sb_count = 0  # SbCount       (int)
    b_sum = 0  # BSum          (int)   Sum of LbCount and SbCount
    alarm_large = 0  # AlarmLarge    (int)
    alarm_small = 0  # AlarmSmall    (int)
    alarm_sum = 0  # AlarmSum      (int)
    reset = 0  # Reset         (int)   Reset command (1 to reset the LbCount counter)
    bb_mass = 6535  # Bbmass        (int)
    sb_mass = 6535  # Sbmass        (int)
    mb_mass = 13070  # Mbmass        (int)   Sum of Bbmass and Sbmass
    mass_set = 6535  # massSet       (int)
    set_max_lb = 6535  # SetMaxLb      (int)
    set_max_sb = 6535  # SetMaxSb      (int)
    set_max_b_sum = 6535  # SetMaxBSum    (int)

    def get_mem_map(self):
        return (
            self.equip_stat,
            self.lb_count,
            self.sb_count,
            self.b_sum,
            self.alarm_large,
            self.alarm_small,
            self.alarm_sum,
            self.reset,
            self.bb_mass,
            self.sb_mass,
            self.mb_mass,
            self.mass_set,
            self.set_max_lb,
            self.set_max_sb,
            self.set_max_b_sum
        )

    def get_first_mem_map(self):
        return (
            self.equip_stat,
            self.lb_count,
            self.sb_count,
            self.b_sum,
            self.alarm_large,
            self.alarm_small,
            self.alarm_sum,
        )

    def get_second_mem_map(self):
        return (
            self.bb_mass,
            self.sb_mass,
            self.mb_mass,
            self.mass_set,
            self.set_max_lb,
            self.set_max_sb,
            self.set_max_b_sum
        )


class Indexes:
    EquipStat = 0
    LbCount = 1
    SbCount = 3
    BSum = 4
    AlarmLarge = 5
    AlarmSmall = 6
    AlarmSum = 7
    Reset = 8
    Bbmass = 9
    Sbmass = 10
    Mbmass = 11
    massSet = 12
    SetMaxLb = 13
    SetMaxSb = 14
    SetMaxBSum = 15


class Slave:

    def __init__(self, slave_id, block_name, refresh_rate, port, ip, file, mem):
        self.slave_id = slave_id
        self.block_name = block_name
        self.refresh_rate = refresh_rate
        self.modbusServ = modbus_tcp.TcpServer(port, ip, self.slave_id)
        self.file = file
        self.mem = mem
        print(Text().color("green", "TCP Server Start \r\n"))
        self.modbusServ.start()
        print(Text().color("blue", "Set slave {} and add block {} \r\n".format(str(self.slave_id), self.block_name)))
        self.slave = self.modbusServ.add_slave(self.slave_id)
        self.slave.add_block(self.block_name, cst.HOLDING_REGISTERS, 0, 21)

    def set_reset(self):
        master_reset = self.slave.get_values(self.block_name, Indexes().Reset, 1)[0]
        if master_reset != self.mem.reset:
            self.mem.reset = master_reset

    def set_counter(self):
        stored_count = self.file.get_int(self.mem.lb_count)
        if self.mem.lb_count != stored_count:
            self.mem.lb_count = stored_count
            print(Text().color("yellow", "Update counter to: {} \r\n".format(str(self.mem.lb_count))))

    def is_reset(self):
        if self.mem.reset == 1 and self.mem.lb_count > 0:
            self.file.reset()
            self.mem.lb_count = self.file.get_int(self.mem.lb_count)
            print(Text().color("red", "Reset counter to: {} \r\n".format(str(self.mem.lb_count))))
            return True
        return False

    def communicate(self):
        print(Text().color("green", "Modbus Server Waiting for client queries...: \r\n"))
        while True:
            print(Text().color("green", "MemMap: {} \r\n".format(str(self.mem.get_mem_map())), True))
            # self.slave.set_values(self.block_name, Indexes().EquipStat, self.mem.get_first_mem_map())
            # self.slave.set_values(self.block_name, Indexes().Bbmass, self.mem.get_second_mem_map())
            self.set_reset()
            if self.is_reset():
                print(Text().color("red", "Reset has been set...: \r\n"))
                # self.slave.set_values(self.block_name, Indexes().Reset, self.mem.reset)
                continue
            self.set_counter()
            time.sleep(self.refresh_rate)


class RoboflowOakWrapper:

    def __init__(self, confidence, version, model, overlap, api_key):
        """
        Creates a RoboflowOak instance
        """
        self.rfo = RoboflowOak(
            confidence=confidence,
            version=version,
            model=model,
            overlap=overlap,
            api_key=api_key,
            rgb=True,
            depth=False,
            device=None,
            blocking=True
        )
        self.centroid_x = 0
        self.centroid_y = 0
        self.width = 0
        self.height = 0

    def set_sizes(self, centroid):
        self.centroid_x = centroid["x"]
        self.centroid_y = centroid["y"]
        self.width = centroid["width"]
        self.height = centroid["height"]
        # self.confidence = centroid["confidence"]

    def get_predictions(self, visualize=True):
        detector = self.rfo.detect(visualize=visualize)
        predictions = detector[DATA]["predictions"]
        return predictions, detector[FRAME]

    def get_rect(self):
        start_x = self.centroid_x - (self.width / 2)
        start_y = self.centroid_y - (self.height / 2)
        end_x = self.centroid_x + (self.width / 2)
        end_y = self.centroid_y + (self.height / 2)
        return start_x, start_y, end_x, end_y

    def get_radius(self):
        return (self.width / 2 + self.height / 2) / 2


class ObjectCounter:

    def __init__(self, centroid_tracker, roboflow_oak_wrapper, file,
                 threshold_from, threshold_to,
                 line_color, thickness, width):
        self.tracker = centroid_tracker
        self.rfw = roboflow_oak_wrapper
        self.file = file
        self.counter = self.file.get_int()
        self.current_counter = self.counter
        self.predictions = self.rfw.get_predictions()
        self.threshold_from = threshold_from
        self.threshold_to = threshold_to
        self.line_color = line_color
        self.thickness = thickness
        self.screen_width = width

    def track(self):
        print(Text().color("green", "current count: {}".format(self.current_counter), True))
        while True:
            self.predictions = self.rfw.get_predictions()
            self.update_counter()
            self.render_image()
            if cv2.waitKey(1) == ord("q"):
                break
            if self.current_counter != self.counter:
                print(Text().color("green", "current count: {}".format(self.counter), True))
                self.current_counter = self.counter

    def update_counter(self):
        (rect, radiis) = self.get_rect_radiis()
        tracker_count = self.tracker.update(rect, radiis)
        self.counter = tracker_count
        if self.counter != tracker_count:
            self.file.set_int(self.counter)

    def get_rect_radiis(self):
        rect = []
        radiis = []
        for raw_prediction in self.predictions[DATA]:
            centroid = raw_prediction.json()
            if self.threshold_from > centroid["y"] or centroid["y"] > self.threshold_to:
                continue
            self.rfw.set_sizes(centroid)
            rect.append(self.rfw.get_rect())
            radiis.append(self.rfw.get_radius())
        return rect, radiis

    def render_image(self):
        image = self.predictions[FRAME]
        self.render_threshold(image)
        cv2.imshow("frames", image)

    def render_threshold(self, image):
        cv2.line(
            image,
            (0, self.threshold_from),
            (self.screen_width, self.threshold_from),
            self.line_color,
            self.thickness
        )
        cv2.line(
            image,
            (0, self.threshold_to),
            (self.screen_width, self.threshold_to),
            self.line_color,
            self.thickness
        )


class CentroidTracker:
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

    def update(self, rect, radii):
        # check to see if the list of input bounding box rectangles
        # is empty
        if len(rect) == 0:
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
            return self.count

        input_centroids = numpy.zeros((len(rect), 2), dtype="int")
        # 		print(input_centroids.shape)
        input_radii = numpy.zeros((len(rect), 1), dtype="int")

        # loop over the bounding box rectangles
        for (i, (startX, startY, endX, endY)) in enumerate(rect):
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
            c_distance = distance.cdist(numpy.array(object_centroids), input_centroids)

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

        return self.count


class Text:
    time_format = "[%Y-%m-%d|%H:%M:%S] "
    reset = '\33[0m'
    colors = {
        "bold": '\33[1m',
        "italic": '\33[3m',
        "curl": '\33[4m',
        "blink": '\33[5m',
        "blink2": '\33[6m',
        "selected": '\33[7m',
        "black": '\33[30m',
        "red": '\33[31m',
        "red2": '\33[91m',
        "green": '\33[32m',
        "green2": '\33[92m',
        "yellow": '\33[33m',
        "yellow2": '\33[93m',
        "blue": '\33[34m',
        "blue2": '\33[94m',
        "violet": '\33[35m',
        "violet2": '\33[95m',
        "beige": '\33[36m',
        "beige2": '\33[96m',
        "white": '\33[37m',
        "white2": '\33[97m',
        "grey": '\33[90m',
        "bg_black": '\33[40m',
        "bg_red": '\33[41m',
        "bg_red2": '\33[101m',
        "bg_green": '\33[42m',
        "bg_green2": '\33[102m',
        "bg_yellow": '\33[43m',
        "bg_yellow2": '\33[103m',
        "bg_blue": '\33[44m',
        "bg_blue2": '\33[104m',
        "bg_violet": '\33[45m',
        "bg_violet2": '\33[105m',
        "bg_beige": '\33[46m',
        "bg_beige2": '\33[106m',
        "bg_white": '\33[47m',
        "bg_white2": '\33[107m',
        "bg_grey": '\33[100m'
    }

    def color(self, color, message, add_time=False):
        if add_time:
            return "{}{}{}{}".format(self.colors[color], self.time(), message, self.reset)
        return "{}{}{}".format(self.colors[color], message, self.reset)

    def time(self):
        now = datetime.now()
        return now.strftime(self.time_format)
