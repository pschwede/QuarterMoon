import math

class Point():
    """Simple vector for calculations"""
    #__slots__ = ('x','y')

    def __init__(self, x=1, y=0):
        """Initializes a Point by given x and y coordinates"""
        # TOTO: This class is a bottleneck!
        self.x, self.y = x, y

    def __repr__(self):
        return str(self)

    def __str__(self):
        """Returns a string representation of the Point"""
        return "<Point "+str(self.x)+","+str(self.y)+">"

    def __add__(self, other):
        """Returns the vector sum of Point and other"""
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Returns the vector from other to Point"""
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        """Returns the scalar product of Point and other"""
        return self.x * other.x + self.y * other.y

    def __div__(self, scalar):
        """Returns Point shorten by scalar; reciprocal to resize()."""
        return Point(float(self.x)/scalar, float(self.y)/scalar)

    def __mod__(self, scalar):
        """Returns Point modulo scalar.\n
        Modulo by zero returns copy of Point with int-ed coords"""
        if scalar:
                return Point(int(self.x)%scalar, int(self.y)%scalar)
        return Point(int(self.x), int(self.y))

    def vmod(self, other):
        """Returns modulated coords of Point"""
        return Point(int(self.x)%int(other.x), int(self.y)%int(other.y))

    def resize(self, s):
        """Returns Point scaled by s; reciprocal to __div__"""
        return Point(self.x * s, self.y * s)

    def normed(self): # depreciated: very inaccurate!
        n = abs(self)
        if n == 0:
            return Point()
        return Point(self.x / n, self.y / n)

    def tuplize(self):
        """Returns (x, y)"""
        return (self.x, self.y)

    def __pos__(self):
        """Returns nonflipped Point (how senseless is that!)"""
        return self

    def __neg__(self):
        """Returns Point flipped by 180 degrees."""
        return Point(-self.x, -self.y)

    def __abs__(self):
        """Returns the length of Point"""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def manhattan(self):
        return abs(self.x)+abs(self.y)

    def __len__(self):
        """Returns dimension of Point"""
        return 2

    def squaredabs(self):
        """ Prefere this before __abs__() """
        return self.x * self.x + self.y * self.y

    def __cmp__(self, other):
        return cmp(self.squaredabs(), other.squaredabs())

    def exists(self):
        """Returns true if the length of Point is greater zero.\n
        Notice: This should be faster than len(Point)>1"""
        return self.x or self.y

    def radians(self):
        return math.atan2(self.x, self.y)	#yea y after x because 90deg Rotation

    def degrees(self):
        return math.degrees(self.radians())

    def rotdeg(self, deg):
        return self.rotrad(math.radians(deg))

    def rotrad(self, rad):
        sr = math.sin(rad)
        cr = math.cos(rad)
        return Point(self.x * cr + self.y * sr, -self.x * sr + self.y * cr)


    # faster arithmetics since __init__ isn't used here
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, other):
        self.x *= other.x
        self.y *= other.y
        return self

    def __idiv__(self, scalar):
        self.x /= scalar
        self.y /= scalar
        return self

    def __imod__(self, scalar):
        self.x = int(self.x) % scalar
        self.y = int(self.y) % scalar
        return self

    def norm(self):
        n = abs(self)
        self.x, self.y = self.x / n, self.y / n
        return self

    def muls(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self

    def rotate(self, rad):
        sr = math.sin(rad)
        cr = math.cos(rad)
        self.x, self.y = self.x * cr + self.y * sr, -self.x * sr + self.y * cr
        return self

    def copy(self):
        return Point(self.x, self.y)

class Null(Point):
    def __init__(self):
        super(0,0)

class One(Point):
    def __init__(self):
        super(0,1)

if __name__ == "__main__":
    """Do some testing"""
    a = Point(1.55,2)
    b = Point(3,4)
    print "a=", a, "b=", b
    print "a+b=", a+b
    print "a-b=", a-b
    print "a*b=", a*b
    print "-a=", -a
    print "a.resize(3)=", a.resize(3)
    print "len(a)", len(a)
    print "abs(b)", abs(b)
    print "a/3=", a/3
    print "-a%3=", -a%3
    print "b%3=", b%3
    print "a.radians()", a.radians(), a.degrees()

