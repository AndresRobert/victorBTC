class file:
    """
    Path and the name for the file that will keep
    the count in the system
    """
    path = "src/files"
    name = "counter"


class ctracker:
    """
    Variables for Centroid Tracker logic
    max_disappeared: how many times the ball has
        to be "disappeared" for it to be considered
        out of the screen and hence counted
    start_id: the starting id assigned to the tracked
        objects to identify them internally
    """
    max_disappeared = 6
    start_id = "0"


class rbflow:
    """
    Variables for Roboflow Oak logic
    version: set in the roboflow page
    model: set in the roboflow page
    api_key: set in the roboflow page
    overlap:
    confidence:
    """
    version = "1"
    model = "detector-de-bolas"
    api_key = "fkaFLk1d4dpuuKeSuGgx"  # todo = store key in a better place
    overlap = 0.2
    confidence = 0.55


class ocounter:
    """
    Variables for Centroid Tracker logic
    threshold_from: initial height in the camera
        frame where the objects should be considered
        to be counted by the tracker
    threshold_to: final height in the camera frame
        where the objects should be considered to be
        counted by the tracker
    """
    threshold_from = 150
    threshold_to = 255


class slave:
    """
    Variables for Slave Server logic
    id:
    block_name:
    ip:
    port:
    refresh_rate: rate at which the slave will i/o
        data from and to the master
    """
    id = 12
    block_name = "BlockName"
    ip = "0.0.0.0"
    port = 5020
    refresh_rate = 0.5


class rgb:
    """
    Basic rgb colors to be used in frames
    """
    red = (0, 0, 255)
    green = (0, 255, 0)
    blue = (255, 0, 0)


class line:
    """
    Line attributes, used mainly for threshold
    """
    light = 1
    bold = 2
    strong = 3


class screen:
    """
    Screen attributes
    """
    max_width = 500
