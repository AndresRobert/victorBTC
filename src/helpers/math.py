def getRadius(width, height):
    return (width / 2 + height / 2) / 2


def getRactangle(x, y, width, height):
    start_x = x - (width/2)
    end_x = x + (width/2)
    start_y = y - (height / 2)
    end_y = y + (height / 2)
    return start_x, start_y, end_x, end_y
