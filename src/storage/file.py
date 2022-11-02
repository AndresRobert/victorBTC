def fetchFromFile(fileName):
    with open("src/storage/{}".format(fileName)) as file:
        lines = file.read()
        first = lines.split('\n', 1)[0]

    return int(first)


def storeInFile(fileName, value):
    file = open("src/storage/{}".format(fileName), 'w')
    file.write(str(value))
    file.close()
