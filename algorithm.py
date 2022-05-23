import math


# All variables should be provided in millimeters


class Algorithm:
    def __init__(self, SHOULDER_LENGTH, ELBOW_LENGTH, END_EFFECTOR_LENGTH=0,
                 x_axis_offset=0, y_axis_offset=0, z_axis_offset=0, WAIST_OFFSET=0, SHOULDER_OFFSET=0, ELBOW_OFFSET=0):
        self._SHOULDER_LENGTH = SHOULDER_LENGTH
        self._ELBOW_LENGTH = ELBOW_LENGTH
        self._END_EFFECTOR_LENGTH = END_EFFECTOR_LENGTH

        self._MAX_HYPOTENUSE_LENGTH = self._SHOULDER_LENGTH+self._ELBOW_LENGTH

        self._X_OFFSET = x_axis_offset
        self._Y_OFFSET = y_axis_offset
        self._Z_OFFSET = z_axis_offset

        self._WAIST_OFFSET = WAIST_OFFSET
        self._SHOULDER_OFFSET = SHOULDER_OFFSET
        self._ELBOW_OFFSET = ELBOW_OFFSET

    def _rads_to_degrees(self, rads):
        return (rads*180)/math.pi

    def _degrees_to_rads(self, rads):
        return (rads*math.pi)/180

    def calculate_raw_angles(self, x, y, z):
        waist_rads = math.atan2(y, x)

        if y < 0 and x < 0:
            waist_rads += 2 * math.pi

        waist_degrees = self._rads_to_degrees(waist_rads)

        r = math.sqrt(pow(x, 2) + pow(y, 2))

        hypotenuse = math.sqrt(pow(r, 2) + pow(z, 2))

        if hypotenuse < self._MAX_HYPOTENUSE_LENGTH:
            alfa_1 = math.atan(z / r)
            cos_alfa = (pow(self._ELBOW_LENGTH, 2) - pow(hypotenuse, 2) - pow(self._SHOULDER_LENGTH, 2)) / (
                    -2 * hypotenuse * self._SHOULDER_LENGTH)

            cos_beta = (pow(hypotenuse, 2) - pow(self._SHOULDER_LENGTH, 2) - pow(self._ELBOW_LENGTH, 2)) / (
                    -2 * self._SHOULDER_LENGTH * self._ELBOW_LENGTH)

            shoulder_degrees = self._rads_to_degrees((math.acos(cos_alfa)) + alfa_1)
            elbow_degrees = self._rads_to_degrees(math.acos(cos_beta))

            return waist_degrees, shoulder_degrees, elbow_degrees

        else:
            return None, None, None

    def calculate_angles_with_offsets(self, x, y, z):
        x -= self._X_OFFSET
        y -= self._Y_OFFSET
        z -= self._Z_OFFSET
        print('Z: ', z)

        waist_raw, shoulder_raw, elbow_raw = self.calculate_raw_angles(x, y, z)

        if waist_raw is not None and shoulder_raw is not None and elbow_raw is not None:
            waist_degrees = abs(-self._WAIST_OFFSET + waist_raw)
            if waist_degrees == 360:
                waist_degrees = 0

            shoulder_degrees = abs(self._SHOULDER_OFFSET + shoulder_raw)
            elbow_degrees = abs(self._ELBOW_OFFSET + elbow_raw)

            return waist_degrees, shoulder_degrees, elbow_degrees

        else:
            return None