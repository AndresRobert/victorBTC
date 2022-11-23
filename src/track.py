import cv2
from helpers import objects, rfowrapper, math, log
from storage import file

DATA = 0
FRAME = 1
COUNT = 2
MIN_TRACK = 245
MAX_TRACK = 415

if __name__ == '__main__':

    sml_current_count = file.fetchFromFile("sml_counter")
    lrg_current_count = file.fetchFromFile("lrg_counter")
    log.warn("[INITIAL] small: {} large: {} objects".format(sml_current_count, lrg_current_count))
    rfo = rfowrapper.RFOWrapper()
    sml_obj = objects.Objects(
        max_disappeared=6,
        start_id=0,
        initial_count=sml_current_count
    )
    lrg_obj = objects.Objects(
        max_disappeared=6,
        start_id=0,
        initial_count=lrg_current_count
    )

    while True:
        predictions = rfo.getPredictions()
        sml_rectangle_list = []
        sml_radius_list = []
        lrg_rectangle_list = []
        lrg_radius_list = []
        for raw_prediction in predictions[DATA]:
            box = raw_prediction.json()
            if box["y"] < MIN_TRACK or box["y"] > MAX_TRACK:
                continue
            if box["class"] == "lrg":
                lrg_rectangle_list.append(math.getRactangle(
                    x=box["x"],
                    y=box["y"],
                    width=box["width"],
                    height=box["height"]
                ))
                lrg_radius_list.append(math.getRadius(
                    width=box["width"],
                    height=box["height"]
                ))
            else:
                sml_rectangle_list.append(math.getRactangle(
                    x=box["x"],
                    y=box["y"],
                    width=box["width"],
                    height=box["height"]
                ))
                sml_radius_list.append(math.getRadius(
                    width=box["width"],
                    height=box["height"]
                ))

        sml_tracked_objects = sml_obj.update(
            rectangles=sml_rectangle_list,
            radii=sml_radius_list
        )
        lrg_tracked_objects = lrg_obj.update(
            rectangles=lrg_rectangle_list,
            radii=lrg_radius_list
        )
        if sml_current_count != sml_tracked_objects[COUNT]:
            sml_current_count = sml_tracked_objects[COUNT]
            log.success("[UPDATED] {} small objects".format(sml_current_count))
            file.storeInFile("sml_counter", sml_current_count)
        if lrg_current_count != lrg_tracked_objects[COUNT]:
            lrg_current_count = lrg_tracked_objects[COUNT]
            log.success("[UPDATED] {} large objects".format(lrg_current_count))
            file.storeInFile("lrg_counter", lrg_current_count)

        image = predictions[FRAME]
        cv2.rectangle(image, (0, MIN_TRACK), (640, MAX_TRACK), (0, 255, 0), 2)
        cv2.imshow("frame", image)
        if cv2.waitKey(1) == ord('q'):
            break
