import config
from tools import \
    CentroidTracker as Ct, \
    FileManager as Fm, \
    ObjectCounter, \
    RoboflowOakWrapper as Row

if __name__ == '__main__':

    print("Set local file to {}/{} \r\n".format(
        config.file.path,
        config.file.name
    ))
    file = Fm(
        config.file.path,
        config.file.name
    )

    ObjectCounter(
        centroid_tracker=Ct(
            max_disappeared=config.ctracker.max_disappeared,
            start_id=config.ctracker.start_id,
            initial_count=file.get_int()
        ),
        roboflow_oak_wrapper=Row(
            confidence=config.rbflow.confidence,
            version=config.rbflow.version,
            model=config.rbflow.model,
            overlap=config.rbflow.overlap,
            api_key=config.rbflow.api_key
        ),
        file=file,
        threshold_from=config.ocounter.threshold_from,
        threshold_to=config.ocounter.threshold_to,
        line_color=config.rgb.green,
        thickness=config.line.bold,
        width=config.screen.max_width
    ).track()
