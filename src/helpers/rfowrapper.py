from roboflowoak import RoboflowOak

MODEL_ID = "detector-de-bolas"
OVERLAP = 0.2
API_KEY = "fkaFLk1d4dpuuKeSuGgx"

RESULT = 0
FRAME = 1
DEPTH = 3


class RFOWrapper:

    def __init__(self, confidence=0.55, version="1"):
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
