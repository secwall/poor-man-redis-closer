"""
Simple ring buffer implementation
"""


class RingBuf:
    """
    Simple ring buffer based on list
    """

    def __init__(self, size):
        self.max_size = size
        self.buf = []
        self.cursor = 0
        self.is_full = False

    def add(self, element):
        """
        Append an element to the buffer
        """
        if self.is_full:
            self.buf[self.cursor] = element
            self.cursor = (self.cursor + 1) % self.max_size
        else:
            self.buf.append(element)
            if len(self.buf) == self.max_size:
                self.is_full = True

    def get(self):
        """
        Get elements in order of insertion
        """
        if self.is_full:
            return self.buf[self.cursor:] + self.buf[:self.cursor]
        return self.buf
