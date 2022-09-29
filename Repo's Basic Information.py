from datetime import datetime
import pymysql
import numpy as np

def get_repos_info():
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT owner, repo_name, created_at, forks_count, stars, size FROM repo_info_data WHERE has_bot > '0'"
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

def get_issues_info(issue_type):
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT repo_name, count(DISTINCT issue_number) FROM issue_info WHERE issue_type = %(issue_type)s GROUP BY repo_name "
    values = {"issue_type": issue_type}
    try:
        # 执行SQL语句
        cursor.execute(sql_query,values)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("get_issues_info error:")
        print(e)


def get_comments_info():
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT repo_name, count(DISTINCT comment_id) FROM issue_comment GROUP BY repo_name"
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

repo_list = get_repos_info()
today = datetime.now()
forks = []
stars = []
dp = []
size = []
for repo in repo_list:
    forks.append(repo[3])
    stars.append(repo[4])
    size.append(repo[5])
    dp.append(int((today - repo[2]).total_seconds() / 2592000) - 2)

print(np.median(dp))

print("forks:")
print(int(max(forks)))
print(int(np.mean(forks)))
print(int(np.percentile(forks,50)))
print(int(min(forks)))

print("stars:")
print(int(max(stars)))
print(int(np.mean(stars)))
print(int(np.percentile(stars,50)))
print(int(min(stars)))

print("development period:")
print(int(max(dp)))
print(int(np.mean(dp)))
print(int(np.percentile(dp,50)))
print(int(min(dp)))

print("size:")
print(int(max(size) / 1024))
print(int(np.mean(size) / 1024))
print(int(np.percentile(size,50) / 1024))
print(int(min(size) / 1024))

issue_num = [x[1] for x in get_issues_info("issues")]
print("issue number:")
print(int(max(issue_num)))
print(int(np.mean(issue_num)))
print(int(np.percentile(issue_num,50)))
print(int(min(issue_num)))

pull_num = [x[1] for x in get_issues_info("pull")]
print("pull number:")
print(int(max(pull_num)))
print(int(np.mean(pull_num)))
print(int(np.percentile(pull_num,50)))
print(int(min(pull_num)))

comment_num = [x[1] for x in get_comments_info()]
print("comment number:")
print(int(max(comment_num)))
print(int(np.mean(comment_num)))
print(int(np.percentile(comment_num,50)))
print(int(min(comment_num)))
