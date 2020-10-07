from datetime import datetime

class Logger:
    def __init__(self, fileRoute):
        self.file = open(fileRoute, "w")

    def close(self):
        self.file.close()

    def log(self, message):
        self.file.write("[{0}] {1}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), message))