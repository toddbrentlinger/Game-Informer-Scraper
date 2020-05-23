
class Thumbnail(object):
    def __init__(self, width = 300, height = 169, srcset = []):
        self.width = width
        self.height = height
        self.srcset = srcset

    def __eq__(self, other):
        if self.width != other.width: return False
        if self.height != other.height: return False
        # Srcset
        if len(self.srcset) != len(other.srcset): return False
        else:
            for i in range(len(self.srcset)):
                if self.srcset[i] != other.srcset[i]:
                    return False
        # If method reaches this point, self and other are equal
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def convertToJSON(self):
        return {
            "width": self.width,
            "height": self.height,
            "srcset": self.srcset }
