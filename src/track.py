import cv2
from helpers import objects, rfowrapper, math, log
from storage import file

DATA = 0
FRAME = 1
COUNT = 2
MIN_TRACK = 245
MAX_TRACK = 400

if __name__ == '__main__':

    current_count = file.fetchFromFile("counter")
    log.warn("[INITIAL] {} objects".format(current_count))
    rfo = rfowrapper.RFOWrapper()
    obj = objects.Objects(
        max_disappeared=6,
        start_id=0,
        initial_count=current_count
    )

    while True:
        predictions = rfo.getPredictions()
        rectangle_list = []
        radius_list = []
        for raw_prediction in predictions[DATA]:
            box = raw_prediction.json()
            if box["y"] < MIN_TRACK or box["y"] > MAX_TRACK:
                continue
            rectangle_list.append(math.getRactangle(
                x=box["x"],
                y=box["y"],
                width=box["width"],
                height=box["height"]
            ))
            radius_list.append(math.getRadius(
                width=box["width"],
                height=box["height"]
            ))

        tracked_objects = obj.update(
            rectangles=rectangle_list,
            radii=radius_list
        )
        if current_count != tracked_objects[COUNT]:
            current_count = tracked_objects[COUNT]
            log.success("[UPDATED] {} objects".format(current_count))
            file.storeInFile("counter", current_count)

        image = predictions[FRAME]
        cv2.rectangle(image, (0, MIN_TRACK), (640, MAX_TRACK), (0, 255, 0), 2)
        cv2.imshow("frame", image)
        if cv2.waitKey(1) == ord('q'):
            break
