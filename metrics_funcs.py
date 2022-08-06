import matplotlib.pyplot as plt
import sqlite3


def stat_task():
    labels = []
    values = []
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = '''SELECT title, solved_by FROM tasks'''
    res = c.execute(query)
    for item in res:
        labels.append(item[0])
        values.append(len(item[1].split()))
    fig1, ax1 = plt.subplots()
    plt.title("Количество решений тасков")
    ax1.bar(labels, values, color="g")
    plt.show()
    conn.close()


def stat_student(student_id):
    labels = ["Решено", "Не решено"]
    values = []
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    query = f'''SELECT COUNT(*), (SELECT COUNT(*) FROM tasks) FROM tasks WHERE solved_by LIKE "%{student_id}%"'''
    res_complite = c.execute(query)
    for item in res_complite:
        values.append(item[0])
        values.append(item[1]-item[0])
    fig1, ax1 = plt.subplots()
    plt.title("Количество решённых тасков")
    ax1.pie(values,
            labels=labels,
            wedgeprops=dict(width=0.6),
            colors=["g", "r"],
            autopct='%1.1f%%')
    plt.show()
    conn.close()

