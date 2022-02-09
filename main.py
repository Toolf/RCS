import math
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
    # Ф-ія статистичної щільності розподілу (як гістограма)

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
    498, 76, 2, 269, 346, 491, 483, 124, 
    1051, 218, 707, 339, 40, 21, 723, 3, 
    144, 136, 18, 248, 40, 515, 248, 444,
    305, 146, 672, 641, 39, 234, 478, 475,
    72, 247, 12, 169, 220, 92, 357, 436,
    121, 5, 3, 81, 115, 271, 259, 389, 305,
    518, 382, 89, 189, 392, 11, 568, 78, 
    464, 189, 898, 309, 45, 370, 1358, 173, 
    66, 616, 733, 152, 239, 207, 963, 379, 
    40, 216, 364, 292, 211, 253, 48, 211, 
    380, 55, 495, 302, 299, 100, 253, 173, 
    51, 122, 403, 286, 1258, 37, 127, 492, 
    969, 155, 573,
]

gama = 0.82
p_t = 1328
lambda_t = 200

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