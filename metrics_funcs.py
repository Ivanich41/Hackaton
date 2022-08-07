import matplotlib.pyplot as plt
import sqlite3
from matplotlib.ticker import MaxNLocator
import math

db = "database.db"

def stat_task():
    import numpy as np

    conn = sqlite3.connect(db)
    c = conn.cursor()
    values = []
    labels = []
    query = '''SELECT title, solved_by FROM tasks'''
    res = c.execute(query)
    for item in res:
        labels.append(item[0])
        values.append(len(item[1].split()))
    a = values
    opacity = 0.7
    bar_width = 0.1
    plt.rcParams.update({'font.size': 8})
    plt.xlabel('Задания')
    plt.ylabel('Количество решений')

    yint = range(min(a) if len(a) != 0 else 0, math.ceil(max(a) if len(a) != 0 else 0)+1)
    plt.yticks(yint)
    plt.xticks(range(len(a)),(labels), rotation=90)
    bar1 = plt.bar(np.arange(len(a)) +  bar_width, a, bar_width, align='center', alpha=opacity, color='g')

    # Add counts above the two bar graphs
    for rect in bar1:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0, height, f'{height:.0f}', ha='right', va='bottom')

    plt.tight_layout()
    filename = f"metrics/teacher/teacher_metrics.png"
    plt.savefig(filename)
    conn.close()
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()

    return open(filename, 'rb')


def stat_student(student_id):
    labels = ["Решено", "Не решено"]
    values = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query = f'''SELECT COUNT(*), (SELECT COUNT(*) FROM tasks) FROM tasks WHERE solved_by LIKE "%{student_id}%"'''
    res_complite = c.execute(query)
    plt.rcParams.update({'font.size': 15, 'font.weight': 'bold'})
    for item in res_complite:
        values.append(item[0])
        values.append(item[1]-item[0])
    fig1, ax1 = plt.subplots()
    plt.title("Статистика моих решений")
    ax1.pie(values,
            labels=labels,
            wedgeprops=dict(width=0.6),
            colors=["g", "r"],
            autopct='%1.1f%%')
    filename = f"metrics/students/{student_id}.png"
    plt.savefig(filename)
    conn.close()
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()

    return (open(filename, 'rb'), values[0], values[1])