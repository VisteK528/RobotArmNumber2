import math


class Conversions:
    def _rad_to_deg(self, radians: float):
        """
        Converts radians to degrees
        :returns: -> float
        """
        return radians * 180 / math.pi

    def _deg_to_rad(self, degrees: float):
        """
        Converts degrees to radians
        :returns: -> float
        """
        return degrees * math.pi / 180

    def _microsec_to_sec(self, microseconds):
        """
        Converts microseconds to seconds
        :returns -> float
        """
        return microseconds / 1000000

    def _sec_to_microsec(self, seconds):
        """
        Converts seconds to microseconds
        :returns: -> float
        """
        return seconds * 1000000
