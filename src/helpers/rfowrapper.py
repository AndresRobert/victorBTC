from roboflowoak import RoboflowOak

MODEL_ID = "molinobolas"
OVERLAP = 0.2
API_KEY = "9KAohILa0qgpHUs0vc41"

RESULT = 0
FRAME = 1
DEPTH = 3


class RFOWrapper:

    def __init__(self, confidence=0.40, version="2"):
        self.rfo = RoboflowOak(
            confidence=confidence,
            version=version,
            model=MODEL_ID,
            overlap=OVERLAP,
            api_key=API_KEY,
            rgb=True,
            depth=False,
            device=None,
            blocking=True
        )

    def getPredictions(self):
        detector = self.rfo.detect()
        predictions = detector[RESULT]["predictions"]
        return predictions, detector[FRAME]
