from math import log

"""
- 1
    При **роздільному** резервуванні спочатку обраховуються 
    ймовірності безвідмовної роботи елементів з урахуванням
    їхнього резервування, а потім ймовірність безвідмовної 
    роботи схеми в цілому

- 2
    При **загальному** резервуванні спочатку обраховується ймовірність 
    безвідмовної роботи схеми без резервування (p_system), 
    а потім за допомогою формул паралельного з’єднання 
    ймовірність схеми з резервуванням

- 3
    При **навантаженому** резервуванні резервні елементи працюють
    в режимі основних з самого початку, тому іморність відмови 
    елемента рахується як відмова даного елемента та всіх резервних.
    Тобто за формолою qi*qi_1*...*qi_k = qi^(k+1)

- 4 (?? це працює лише для роздільного ??)
    При **ненавантаженому** резервуванні ймовірність відмови
    в (k+1)! раз менша, ніж при навантаженому. 
"""

def mul(arr):
    r = 1
    for el in arr:
        r *= el
    return r

def get_state(i, n):
    return [1 if (i & (1<<k)) != 0 else 0 for k in range(n)]


class ExistPath:
    def __init__(self, graph):
        self.graph = graph

    def __call__(self, *,from_, to_, through):
        for v in self.graph[from_]:
            if v == to_:
                return True
            if v in through:
                through_ = [vertex for vertex in through if vertex != v]
                if self(from_=v, to_=to_, through=through_):
                    return True
        return False


class PState:
    def __init__(self, P):
        self.P = P
        self.Q = [1-pi for pi in P]
        
    def __call__(self, s):
        return mul([
            self.P[i] if si == 1 else self.Q[i]
            for i,si in enumerate(s) 
        ])


class Workable:
    def __init__(self, graph, start, end):
        self.start = start
        self.end = end
        self.exist_path = ExistPath(graph)

    def __call__(self, s):
        through = [i+1 for i,si in enumerate(s) if si == 1]
        return self.exist_path(
            from_=self.start,
            to_=self.end,
            through=through
        )
        

def factorial(n):
    return mul(range(1, n+1))

# ========== Вхідні дані за варіантом ==============

n = 8
start_index = 0
end_index = n+1

G = {
    0: [1, 2],          # start
    1: [0, 2, 3, 5],    # 1
    2: [0, 1, 4, 7],    # 2
    3: [1, 4, 5],       # 3
    4: [2, 3, 7],       # 4
    5: [1, 3, 6],       # 5
    6: [5, 8, 9],       # 6
    7: [2, 4, 8],       # 7
    8: [6, 7, 9],       # 8
    9: [6, 8],          # end
}

P = [
    0.00,
    0.08,
    0.12,
    0.21,
    0.12,
    0.27,
    0.84,
    0.12,
]

Q = [1-pi for pi in P]

T = 2251

k1 = 2
k2 = 1

# ==================================================

# ================ Підготовка ф-ій =======================
workable = Workable(G, start_index, end_index)
p_state = PState(P)
# ========================================================

# ====== Дані з попередньої лабораторної ========
all_states = [get_state(i, n) for i in range(2**n)]
workable_states = [*filter(workable, all_states)]

p_system = sum([p_state(state) for state in workable_states])
q_system = 1 - p_system
t_system = -T / log(p_system)
print("========== Дані системи без резервування ==========")
print(f"{p_system = }")
print(f"{q_system = }")
print(f"{t_system = }")
# ===============================================

# Загальне навантаженне
def generalLoaded(k, T, p_system):
    p_reserved_system = 1 - (1 - p_system)**(k+1)
    q_reserved_system = 1 - p_reserved_system
    t_reserved_system = -T / log(p_reserved_system)

    return p_reserved_system, q_reserved_system, t_reserved_system

# Загальне ненавантажене
def generalNonloaded(k, T, p_system):
    p_reserved_system = 1 - (1 - p_system) / factorial(k+1)
    q_reserved_system = 1 - p_reserved_system
    t_reserved_system = -T / log(p_reserved_system)

    return p_reserved_system, q_reserved_system, t_reserved_system

# Роздільне навантажене
def seperativeLoaded(k, T, Q, workable_states):
    Q_reserved = [qi**(k+1) for qi in Q]
    P_reserved = [1-qr for qr in Q_reserved]
    p_reserved_state = PState(P_reserved)

    p_reserved_system = sum([
        p_reserved_state(state) 
        for state in workable_states
    ])
    q_reserved_system = 1 - p_reserved_system
    t_reserved_system = -T / log(p_reserved_system)

    return p_reserved_system, q_reserved_system, t_reserved_system

# Роздільне ненавантажене
def seperativeNonloaded(k, T, Q, workable_states):
    Q_reserved = [qi**(k+1) for qi in Q]
    P_reserved = [1-qr for qr in Q_reserved]
    p_reserved_state = PState(P_reserved)

    p_reserved_system = 1 - 1 / factorial(k + 1) * (1 - sum([
        p_reserved_state(state) 
        for state in workable_states
    ]))
    q_reserved_system = 1 - p_reserved_system
    t_reserved_system = -T / log(p_reserved_system)

    return p_reserved_system, q_reserved_system, t_reserved_system


# ================== Виконання завдання ===================
print(f"========== Загальне навантаженне (k={k1}) ==========")

p_reserved_system, q_reserved_system, t_reserved_system = \
    generalLoaded(k1, T, p_system)

print(f"{p_reserved_system = }")
print(f"{q_reserved_system = }")
print(f"{t_reserved_system = }")
print(f"Gp = {p_reserved_system / p_system}")
print(f"Gq = {q_reserved_system / q_system}")
print(f"Gt = {t_reserved_system / T}")


print(f"========== Загальне ненавантаженне (k={k2}) ==========")
p_reserved_system, q_reserved_system, t_reserved_system = \
    generalNonloaded(k2, T, p_system)
print(f"{p_reserved_system = }")
print(f"{q_reserved_system = }")
print(f"{t_reserved_system = }")
print(f"Gp = {p_reserved_system / p_system}")
print(f"Gq = {q_reserved_system / q_system}")
print(f"Gt = {t_reserved_system / T}")

# print(f"========== Роздільне навантажене (k={1}) ==========")
# p_reserved_system, q_reserved_system, t_reserved_system = \
#     seperativeLoaded(1, T, Q, workable_states)
# print(f"{p_reserved_system = }")
# print(f"{q_reserved_system = }")
# print(f"{t_reserved_system = }")
# print(f"Gp = {p_reserved_system / p_system}")
# print(f"Gq = {q_reserved_system / q_system}")
# print(f"Gt = {t_reserved_system / T}")

# print(f"========== Роздільне ненавантажене (k={1}) ==========")
# p_reserved_system, q_reserved_system, t_reserved_system = \
#     seperativeNonloaded(1, T, Q, workable_states)
# print(f"{p_reserved_system = }")
# print(f"{q_reserved_system = }")
# print(f"{t_reserved_system = }")
# print(f"Gp = {p_reserved_system / p_system}")
# print(f"Gq = {q_reserved_system / q_system}")
# print(f"Gt = {t_reserved_system / T}")

# # =========================================================