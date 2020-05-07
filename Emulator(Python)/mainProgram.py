from array import *
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import numpy as np

import serial

ser = serial.Serial("COM4", 9600)

# Константы
EPS = 2
mass_karetka = 0.047
mass_shaiba = 0.220
mass_gruz = 0.408
l_1 = 5.7
l_0 = 2.5
b = 4.0
d = 4.6
h_0 = 70.0
g = 9.81908
humanDelayTime = 0.13
I_0 = 0.011541518
M_tr_a = 0.003179657
M_tr_b = 0.000950262
moments_tr = [-0.00228920, 0.00998837, 0.00906186, 0.01317346, 0.01499408, 0.01614266]

# Переменные
n = 0  # Номер рейки
q = 0  # Колличество грузов


# =======================================================================================================================

def showPlot(x_, y_):
    plt.figure()
    plt.plot(x_, y_)
    plt.show()


def M_tr(n_):
    global moments_tr
    return moments_tr[n_ - 1]


def R(n_):
    global l_1
    global l_0
    global b
    return l_1 + (n_ - 1) * l_0 + b / 2


def I(n_):
    global I_0
    global mass_gruz
    return I_0 + 4 * mass_gruz * R(n_) * R(n_) / 10000


def m(q_):
    global mass_karetka
    global mass_shaiba
    return mass_karetka + q_ * mass_shaiba


def a(q_, n_):
    global d
    global g
    return (m(q_) * (d / 100) * g / 2 - M_tr(n_)) / (2 * I(n_) / (d / 100) + m(q_) * (d / 100) / 2)


def x(t_, q_, n_):
    global h_0
    return 100.0 * max(0, h_0 / 100 - a(q_, n_) * t_ * t_ / 2)


def check_facility_settings():
    global mass_karetka
    global mass_shaiba
    global mass_gruz
    global l_1
    global l_0
    global d
    global b

    print("Желаете ли внести изменить данные об установке?\n 1 - Да, 2 - Нет")
    changeInstallationData = int(input())
    if changeInstallationData == 1:
        print("Введите массу каретки: ", end="")
        mass_karetka = float(input())
        print("Введите массу шайбы: ", end="")
        mass_shaiba = float(input())
        print("Введите массу груза-утяжелителя на крестовине: ", end="")
        mass_gruz = float(input())
        print("Введите расстояние первой риски от оси: ", end="")
        l_1 = float(input())
        print("Введите расстояние между рисками: ", end="")
        l_0 = float(input())
        print("Введите диаметр ступицы: ", end="")
        d = float(input())
        print("Введите размер утяжелителя вдоль спицы: ", end="")
        b = float(input())


def set_N_and_Q():
    global n
    global q

    print("======================================================")
    print("Выберите конфигурацию:\nГрузы: 1, 2, 3, 4\nРейка: 1, 2, 3, 4, 5, 6");

    print("Введите колличество грузов: ", end="")
    q = int(input())
    print("Введите номер риски: ", end="")
    n = int(input())
    print("======================================================")


# ======================== Эмулятор ========================
def get_single_measurement_Emulator():
    global n
    global q

    set_N_and_Q()

    measurements = []

    r = 70.0
    experimentTime = 0.0
    while r > 0.0:
        measurements.append(r)
        r = x(experimentTime, q, n)
        experimentTime += 0.01
    # Эвристика
    fall_time = 0.01 * len(measurements) - 0.1

    return fall_time


def make_calculations_Emulator():
    # TODO Результаты

    th = [...]  # Шапка
    td = [...]  # Данные

    columns = len(th)

    table = PrettyTable(th)

    td_data = td[:]

    while td_data:
        table.add_row(td_data[:columns])
        td_data = td_data[columns:]

    print(table)


# ======================== Установка ========================

def get_single_measurement_Arduino():
    global n
    global q

    set_N_and_Q()
    ser.write(("throw " + n + " " + q).encode("utf-8"))

    arduino_data = []

    t_in = ser.readline()
    t_in = ser.readline()

    data_initial = 70.0
    data_in = 70.0

    if len(t_in) == 7:
        data_in = (t_in[0] - 48) * 10 + (t_in[1] - 48) + (t_in[2] - 48) / 10 + (t_in[3] - 48) / 100
    elif len(t_in) == 6:
        data_in = (t_in[0] - 48) + (t_in[1] - 48) / 10 + (t_in[2] - 48) / 100
    else:
        data_initial = 0.0

    f1 = True
    while f1:
        t_in = ser.readline()

        if len(t_in) == 7:
            data_in = (t_in[0] - 48) * 10 + (t_in[1] - 48) + (t_in[2] - 48) / 10 + (t_in[3] - 48) / 100
        elif len(t_in) == 6:
            data_in = (t_in[0] - 48) + (t_in[1] - 48) / 10 + (t_in[2] - 48) / 100
        else:
            data_in = 0.0

        if abs(data_initial - data_in) < EPS:
            f1 = False

    while data_in > 0.0:
        t_in = ser.readline()

        if len(t_in) == 7:
            data_in = (t_in[0] - 48) * 10 + (t_in[1] - 48) + (t_in[2] - 48) / 10 + (t_in[3] - 48) / 100
        elif len(t_in) == 6:
            data_in = (t_in[0] - 48) + (t_in[1] - 48) / 10 + (t_in[2] - 48) / 100
        else:
            data_in = 0.0

        arduino_data.append(data_in)

    return arduino_data


def make_calculations_Arduino():
    # TODO Результаты
    th = [...]  # Шапка
    td = [...]  # Данные

    columns = len(th)

    table = PrettyTable(th)

    td_data = td[:]

    while td_data:
        table.add_row(td_data[:columns])
        td_data = td_data[columns:]

    print(table)


# =======================================================================================================================

print("======================================================")
print("Добро пожаловать!")

check_facility_settings()

command = 1
while command == 1:
    print("Выберите действие")
    print("=== Эмулятор ===")
    print("1 - Одиночное измерение (эмулятор)")
    print("2 - Серия измерений для каждого положения груза на рейки и масс шайбы (эмулятор)")
    print("=== Установка ===")
    print("3 - Одиночное измерение (установка)")
    print("4 - Серия измерений для каждого положения груза на рейки и масс шайбы (установка)")
    print("=== Выход ===")
    print("5 - Закончить программу")

    command = int(input())

    if command == 1:
        fall_time = get_single_measurement_Emulator()

        print("Время падаения равно ", end="")
        print(fall_time)

    elif command == 2:
        make_calculations_Emulator()

    elif command == 3:
        arduino_data = get_single_measurement_Arduino()

        print("Время падаения равно ", end="")
        print(0.01 * len(arduino_data))

    elif command == 4:
        make_calculations_Arduino()

    else:
        print("Неверно введена команда!\n")