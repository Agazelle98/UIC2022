import pymysql
from collections import defaultdict
def get_repos_info():
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT owner, repo_name FROM repo_info_data WHERE has_bot > '0'"
    try:
        # 执行SQL语句
        cursor.execute(sql_query)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("get_repos_inf error:")
        print(e)

def get_comments_info(bot_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT DISTINCT comment FROM issue_comment WHERE commenter = '" + bot_name + "' ORDER BY comment"
    try:
        # 执行SQL语句
        cursor.execute(sql_query)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("get_comments_info error:")
        print(e)

def get_bots_info():
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT bot_name FROM bot_info_data WHERE template > '19'"
    try:
        # 执行SQL语句
        cursor.execute(sql_query)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("get_bots_inf error:")
        print(e)

def insert_into_bot_info(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "UPDATE bot_info_data SET template = (%s) WHERE bot_name = (%s)"
    try:
        # 执行SQL语句
        cursor.execute(sql_query, value)
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("insert_pr error:")
        print(e)

def min(a,b):
    if a < b:
        return a
    else:
        return b

bot_list = [x[0] for x in get_bots_info()]

#统计模板，分别查找前两位相同的、中间几位相同的、最后几位相同的，如果这三个相等，则模板数确定，如不等，选最少的那个


for bot in bot_list:
    comment_list = get_comments_info(bot)
    first = []
    last = []
    for comment in comment_list:
        first.append(comment[0][0:2])
        last.append(comment[0][-3:-1])


    first = list(set(first))
    last = list(set(last))
    first.sort()
    last.sort()
    final_first = []
    for ele in first:
        count = 0
        for comment in comment_list:
            if comment[0][0:2] == ele:
                count = count + 1
        if count > 10:
            final_first.append(ele)

    final_last = []
    for ele in last:
        count = 0
        for comment in comment_list:
            if comment[0][-3:-1] == ele:
                count = count + 1
        if count > 10:
            final_last.append(ele)

    template_num = len(final_first) if len(final_first) == len(final_last) else min(len(final_first), len(final_last))
    print(bot + " : " + str(template_num))
    print(first)
    print(last)
    insert_into_bot_info([template_num, bot])