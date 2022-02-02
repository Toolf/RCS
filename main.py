import math
from decimal import *
import matplotlib.pyplot as plt


# =========== Utils ========== 
def avarage(values):
    return sum(values)/len(values)

def count(ls, cond):
    return sum([cond(elem) for elem in ls])

def in_interval(start, end):
    def f(t):
        return start <= t <= end

    return f

def Ni(ti, interval_start, interval_end):
    return count(ti, in_interval(interval_start, interval_end))

# =========== Utils end ============



class FStar:
    def __init__(self, ts, steps = 10):
        t_max = max(ts)
        h = t_max / steps
        N = len(ts)
        self.fs = [
            Ni(ts, part*h, (part + 1)*h)/ (N * h)
            for part in range(0, steps)
        ]
        self.h = h

    def __call__(self, t):
        part = math.floor(t / self.h)
        
        if (part < 0 or len(self.fs) <= part):
            raise Exception("Unknown interval")

        return self.fs[part] 

    def integral(self, start, end):
        if start > end:
            raise Exception(f"Invalid interval from {start} to {end}")
        start = max(start, 0)
        end = min(end, len(self.fs) * self.h)
        
        _start = math.floor(start / self.h) * self.h
        _end = math.ceil(end / self.h) * self.h

        _start_index = math.floor(start / self.h)
        _end_index = math.ceil(end / self.h) - 1

        return sum(self.fs[_start_index:_end_index+1]) * self.h \
            - (
                (_end - end)*self.fs[_end_index] 
                if _end_index  < len(self.fs) else 0
            ) \
            - (
                (start - _start)*self.fs[_start_index] 
                if _start_index < len(self.fs) else 0
            )
            

class QStar:
    def __init__(self, f):
        self.f = f

    def __call__(self, t):
        return self.f.integral(0, t)

class PStar:
    def __init__(self, f):
        self.f = f

    def __call__(self, t) -> float:
        return 1 - self.f.integral(0, t)


class LambdaStar:
    def __init__(self, ts, steps=10):
        self.f = FStar(ts, steps=steps)
        self.p = PStar(self.f)
    
    def __call__(self, t):
        return self.f(t) / self.p(t)

class GamaStar:
    def __init__(self, ts, steps=10):
        self.ts = ts
        self.h = max(ts) / steps
        self.steps = steps
        self.f = FStar(ts, steps=steps)
        self.p = PStar(self.f)
        
    def __call__(self, gama):
        if gama < 0 or gama > 1:
            raise Exception(f"Invalid gama value, {gama=}")
        
        h = self.h
        i = 0
        while self.p(i*h) > gama:
            i+=1
        ti = i * h
        ti_ = (i - 1) * h

        return ti - h*self.d(ti, ti_, gama)

    def d(self, ti, ti_, gama):
        return (self.p(ti) - gama) / (self.p(ti) - self.p(ti_))



PART_COUNT = 10

ts = [
    644, 1216, 2352, 1386, 1280, 903, 607, 2068,
    4467, 835, 313, 555, 307, 508, 1386, 2895, 583,
    292, 5159, 1107, 181, 18, 1247, 125, 1452, 4211,
    890, 659, 1602, 2425, 214, 68, 21, 1762, 1118,
    45, 1803, 1187, 2154, 19, 1122, 278, 1622, 702,
    1396, 694, 45, 1739, 3483, 1334, 1852, 96, 173,
    7443, 901, 2222, 4465, 18, 1968, 1426, 1424,
    1146, 435, 1390, 246, 578, 281, 455, 609, 854,
    436, 1762, 444, 466, 1934, 681, 4539, 164, 295,
    1644, 711, 245, 740, 18, 474, 623, 462, 605, 187,
    106, 793, 92, 296, 226, 63, 246, 446, 2234, 2491,
    315,
]

ts.sort()

gama = 0.9
p_t = 2000
labda_t = 2000


f_star = FStar(ts, steps=PART_COUNT)
p_star = PStar(f_star)
lambda_star = LambdaStar(ts, steps=PART_COUNT)
gama_star = GamaStar(ts, steps=PART_COUNT)

print(f"Середній наробіток до відмови: {avarage(ts)}")
print(f"Гама відсотоковий наробітку на відмову: {gama_star(gama)}")
print(f"Ймовірність безвідмовної роботи: {p_star(p_t)}")
print(f"Інтенсивність відмови: {lambda_star(labda_t)}")


h = max(ts) / PART_COUNT
x = [*range(PART_COUNT)]
y = [f_star(i*h) for i in x]

plt.plot(x, y)
plt.show()