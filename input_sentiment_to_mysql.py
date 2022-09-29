import os
import csv
import pymysql
import datetime,time

file_dir = 'C:\\Users\\76446\\Desktop\\res\\'
dir_list = os.listdir(file_dir)

def insert_into_mysql(input_list):
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # SQL 插入语句
    sql = "UPDATE issue_comment SET sentiment = (%s) WHERE comment_id = (%s)"

    # 使用 execute()  方法执行 SQL 查询
    try:
        # 执行sql语句
        cursor.executemany(sql,input_list)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        print("ERR0R:")
        print(e)
    # 关闭数据库连接
    db.close()

for file in dir_list:
    start_time =datetime.datetime.now()
    print(start_time)
    id_list = []
    pre_list = []
    with open('C:\\Users\\76446\\Desktop\\res\\28789.csv', 'r+', newline='', encoding='utf8') as csv_file:
        csv_file.seek(0)
        csv_file_reader = csv.reader(csv_file, delimiter=',')
        next(csv_file_reader)
        for row in csv_file_reader:
            id_list.append(row[0])
            pre_list.append(row[1])
        input_list = [[pre_list[i], id_list[i]] for i in range(len(id_list))]
        insert_into_mysql(input_list)
    end_time = datetime.datetime.now()
    print(end_time)