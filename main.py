import math
from decimal import *
import matplotlib.pyplot as plt


# =========== Utils ========== 
def average(values):
    return sum(values)/len(values)

def count(ls, cond):
    return sum([cond(elem) for elem in ls])

def in_interval(start, end):
    def f(t):
        return start < t <= end

    return f

def Ni(ts, interval_start, interval_end):
    return count(ts, in_interval(interval_start, interval_end))

# =========== Utils end ============



class FStar:
    # Ф-ія статистичної щільністі розподілу (як гістограма)

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

        if (t == t_max):
            return self.fs[-1]
        
        if (part < 0 or len(self.fs) <= part):
            raise Exception(f"Unknown interval {t=} {part=}")

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
            

class Q:
    # Ф-ія імовірності відмови
    
    def __init__(self, f):
        self.f = f

    def __call__(self, t):
        return self.f.integral(0, t)


class P:
    # Ф-ія безвідмовної роботи

    def __init__(self, f):
        self.f = f

    def __call__(self, t) -> float:
        return 1 - self.f.integral(0, t)


class LambdaStar:
    # Ф-ія інтенсивність відмови

    def __init__(self, ts, steps=10):
        self.f = FStar(ts, steps=steps)
        self.p = P(self.f)
    
    def __call__(self, t):
        return self.f(t) / self.p(t)


class GamaStar:
    # Ф-ія гама-фідсоткового наробітку на відмову

    def __init__(self, ts, steps=10):
        self.ts = ts
        self.h = max(ts) / steps
        self.steps = steps
        self.f = FStar(ts, steps=steps)
        self.p = P(self.f)
        
    def __call__(self, gama):
        if gama <= 0 or gama > 1:
            raise Exception(f"Invalid gama value, {gama=}")
        
        h = self.h
        i = 0
        while self.p(i*h) >= gama and self.p(i*h) != 0:
            i+=1

        ti = i * h
        ti_ = (i - 1) * h
        
        return ti - h*self.d(ti, ti_, gama)

    def d(self, ti, ti_, gama):
        return (self.p(ti) - gama) / (self.p(ti) - self.p(ti_))




# ========== Дані за варіантом ================
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

gama = 0.9
p_t = 2000
lambda_t = 2000

# Відсортуємо для зручності часи відмови
ts.sort()
t_max = max(ts)
# ==================================================

# =========== Підготовка основних ф-ій =============
f_star = FStar(ts, steps=PART_COUNT)
q_star = Q(f_star)
p_star = P(f_star)
lambda_star = LambdaStar(ts, steps=PART_COUNT)
gama_star = GamaStar(ts, steps=PART_COUNT)
# ==================================================

# ============== Вивід результатів виконання завдання ============
print(f"Середній наробіток до відмови: {average(ts)}")
print(f"Гама відсотоковий наробітку на відмову ({gama=}): {gama_star(gama)}")
print(f"Ймовірність безвідмовної роботи протягом {p_t}: {p_star(p_t)}")
print(f"Інтенсивність відмови за час {lambda_t}: {lambda_star(lambda_t)}")
# ================================================================

# ============= Вивід результатів в графічному вигляді ===============
x = [*range(t_max+1)]
f_y = [f_star(xi) for xi in x]
p_y = [p_star(xi) for xi in x]
q_y = [q_star(xi) for xi in x]
gama_x = [*map(lambda x: x/100,range(1, 101))]
gama_y = [gama_star(gama_i) for gama_i in gama_x]

fig, axs = plt.subplots(2, 2)
axs[0, 0].plot(x, f_y)
axs[0, 0].set_title('F*(t)')
axs[0, 1].plot(x, p_y, 'tab:orange')
axs[0, 1].set_title('P*(t)')
axs[1, 0].plot(x, q_y, 'tab:green')
axs[1, 0].set_title('Q*(t)')
axs[1, 1].plot(gama_x, gama_y, 'tab:red')
axs[1, 1].set_title('T_gama(gama)')

plt.show()
# =====================================================================