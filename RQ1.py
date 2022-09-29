import pymysql
from numpy import *
from scipy import stats
import numpy as np
import datetime

def get_repos_info():
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT owner, repo_name FROM repo_info_data"
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

def get_bots_info():
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT bot_name FROM bot_info_data"
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

def get_issues_info(owner, repo_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT issue_url,issue_proposer,issue_state,created_at,updated_at,issue_type FROM issue_info WHERE repo_owner = %(repo_owner)s AND repo_name = %(repo_name)s"
    values = {"repo_owner": owner, "repo_name": repo_name}
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

def get_comments_info(owner, repo_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT url, commenter, sentiment FROM issue_comment WHERE owner = %(repo_owner)s AND repo_name = %(repo_name)s ORDER BY updated_at"
    values = {"repo_owner": owner, "repo_name": repo_name}
    try:
        # 执行SQL语句
        cursor.execute(sql_query,values)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("get_comments_info error:")
        print(e)

"""RQ1.1
1.bot提出的issue/pr下开发者情感
2.human提出的issue/pr下开发者情感
RQ1.2
3.bot参与前后开发者情感有什么差异（提取出放入新表）
RQ2
4.issue/pr解决时间与情感是否有关"""

def search_comments(num, comment_list):
    comments_temp = []
    for comment in comment_list:
        if comment[0].split('/')[-1] == num:
            comments_temp.append(comment)
    return comments_temp

def transfer_to_score(sentiment_list):
    sentiment_temp = []
    for sentiment in sentiment_list:
        if sentiment == 'neutral':
            sentiment_temp.append(0)
        elif sentiment == 'positive':
            sentiment_temp.append(1)
        elif sentiment == 'negative':
            sentiment_temp.append(-1)
    return sentiment_temp

def get_p_value(arrA, arrB):
  a = np.array(arrA)
  b = np.array(arrB)
  t, p = stats.ttest_ind(a,b)
  return p

repo_list = get_repos_info()
bot_list = [x[0] for x in get_bots_info()]

bot_created_issues_sentiment = []
human_created_issues_sentiment = []
bot_created_pulls_sentiment = []
human_created_pulls_sentiment = []

bot_invol_issues_sentiment = []
bot_invol_pulls_sentiment = []
wo_bot_invol_issues_sentiment = []
wo_bot_invol_pulls_sentiment = []

b_bot_invol_issues_sentiment = []
a_bot_invol_issues_sentiment = []
b_bot_invol_pulls_sentiment = []
a_bot_invol_pulls_sentiment = []

not_included = []

for repo in repo_list:
    start = datetime.datetime.now()
    issue_list = get_issues_info(repo[0],repo[1])
    comment_list = get_comments_info(repo[0],repo[1])
    end = datetime.datetime.now()
    print((end - start).seconds)

    bot_created_issues = []
    human_created_issues = []
    bot_created_pulls = []
    human_created_pulls = []
    bot_invol_issues = []
    bot_invol_pulls = []

    start = datetime.datetime.now()
    for issue in issue_list:
        if issue[1] in bot_list and issue[5] == 'issues':
            bot_created_issues.append(issue[0].split('/')[-1])
        elif issue[1] not in bot_list and issue[5] == 'issues':
            human_created_issues.append(issue[0].split('/')[-1])
        elif issue[1] in bot_list and issue[5] == 'pull':
            bot_created_pulls.append(issue[0].split('/')[-1])
        elif issue[1] not in bot_list and issue[5] == 'pull':
            human_created_pulls.append(issue[0].split('/')[-1])
    end = datetime.datetime.now()
    print((end - start).seconds)

    start = datetime.datetime.now()
    for comment in comment_list:
        if comment[0].split('/')[-1] in bot_created_issues and comment[1] not in bot_list:
            bot_created_issues_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in human_created_issues and comment[1] not in bot_list:
            human_created_issues_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in bot_created_pulls and comment[1] not in bot_list:
            bot_created_pulls_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in human_created_pulls and comment[1] not in bot_list:
            human_created_pulls_sentiment.append(comment[2])
        else:
            not_included.append(comment)

        if comment[1] in bot_list and comment[0].split('/')[-2] == 'issues':
            bot_invol_issues.append(comment[0].split('/')[-1])
        elif comment[1] in bot_list and comment[0].split('/')[-2] == 'pull':
            bot_invol_pulls.append(comment[0].split('/')[-1])

    end = datetime.datetime.now()
    print((end - start).seconds)

    bot_invol_issues = list(set(bot_invol_issues))
    bot_invol_pulls = list(set(bot_invol_pulls))
    bot_invol_issues_temp = []
    bot_invol_pulls_temp = []

    start = datetime.datetime.now()
    for comment in comment_list:
        if comment[0].split('/')[-1] in bot_invol_issues and comment[0].split('/')[-2] == 'issues' and comment[1] not in bot_list:
            bot_invol_issues_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] not in bot_invol_issues and comment[0].split('/')[-2] == 'issues' and comment[1] not in bot_list:
            wo_bot_invol_issues_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in bot_invol_pulls and comment[0].split('/')[-2] == 'pull' and comment[1] not in bot_list:
            bot_invol_pulls_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] not in bot_invol_pulls and comment[0].split('/')[-2] == 'pull' and comment[1] not in bot_list:
            wo_bot_invol_pulls_sentiment.append(comment[2])

        if comment[1] in bot_list and comment[0].split('/')[-2] == 'issues':
            bot_invol_issues_temp.append(comment[0].split('/')[-1])
        elif comment[1] in bot_list and comment[0].split('/')[-2] == 'pull':
            bot_invol_pulls_temp.append(comment[0].split('/')[-1])
        if comment[0].split('/')[-1] in bot_invol_issues and comment[0].split('/')[-1] not in bot_invol_issues_temp and comment[0].split('/')[-2] == 'issues' and comment[1] not in bot_list:
            b_bot_invol_issues_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in bot_invol_issues and comment[0].split('/')[-1] in bot_invol_issues_temp and comment[0].split('/')[-2] == 'issues' and comment[1] not in bot_list:
            a_bot_invol_issues_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in bot_invol_pulls and comment[0].split('/')[-1] not in bot_invol_pulls_temp and comment[0].split('/')[-2] == 'pull' and comment[1] not in bot_list:
            b_bot_invol_pulls_sentiment.append(comment[2])
        elif comment[0].split('/')[-1] in bot_invol_pulls and comment[0].split('/')[-1] in bot_invol_pulls_temp and comment[0].split('/')[-2] == 'pull' and comment[1] not in bot_list:
            a_bot_invol_pulls_sentiment.append(comment[2])
        else:
            not_included.append(comment)

    end = datetime.datetime.now()
    print((end - start).seconds)

    print(repo[0] + " success!")

bot_created_issues_sentiment = transfer_to_score(bot_created_issues_sentiment)
print('bot_created_issues_sentiment:')
print('positive:' + str(bot_created_issues_sentiment.count(1)))
print('neutral:' + str(bot_created_issues_sentiment.count(0)))
print('negative:' + str(bot_created_issues_sentiment.count(-1)))
human_created_issues_sentiment = transfer_to_score(human_created_issues_sentiment)
print('human_created_issues_sentiment:')
print('positive:' + str(human_created_issues_sentiment.count(1)))
print('neutral:' + str(human_created_issues_sentiment.count(0)))
print('negative:' + str(human_created_issues_sentiment.count(-1)))
bot_created_pulls_sentiment = transfer_to_score(bot_created_pulls_sentiment)
print('bot_created_pulls_sentiment:')
print('positive:' + str(bot_created_pulls_sentiment.count(1)))
print('neutral:' + str(bot_created_pulls_sentiment.count(0)))
print('negative:' + str(bot_created_pulls_sentiment.count(-1)))
human_created_pulls_sentiment = transfer_to_score(human_created_pulls_sentiment)
print('human_created_pulls_sentiment:')
print('positive:' + str(human_created_pulls_sentiment.count(1)))
print('neutral:' + str(human_created_pulls_sentiment.count(0)))
print('negative:' + str(human_created_pulls_sentiment.count(-1)))

bot_invol_issues_sentiment = transfer_to_score(bot_invol_issues_sentiment)
print('bot_invol_issues_sentiment:')
print('positive:' + str(bot_invol_issues_sentiment.count(1)))
print('neutral:' + str(bot_invol_issues_sentiment.count(0)))
print('negative:' + str(bot_invol_issues_sentiment.count(-1)))
bot_invol_pulls_sentiment = transfer_to_score(bot_invol_pulls_sentiment)
print('bot_invol_pulls_sentiment:')
print('positive:' + str(bot_invol_pulls_sentiment.count(1)))
print('neutral:' + str(bot_invol_pulls_sentiment.count(0)))
print('negative:' + str(bot_invol_pulls_sentiment.count(-1)))
wo_bot_invol_issues_sentiment = transfer_to_score(wo_bot_invol_issues_sentiment)
print('wo_bot_invol_issues_sentiment:')
print('positive:' + str(wo_bot_invol_issues_sentiment.count(1)))
print('neutral:' + str(wo_bot_invol_issues_sentiment.count(0)))
print('negative:' + str(wo_bot_invol_issues_sentiment.count(-1)))
wo_bot_invol_pulls_sentiment = transfer_to_score(wo_bot_invol_pulls_sentiment)
print('wo_bot_invol_pulls_sentiment:')
print('positive:' + str(wo_bot_invol_pulls_sentiment.count(1)))
print('neutral:' + str(wo_bot_invol_pulls_sentiment.count(0)))
print('negative:' + str(wo_bot_invol_pulls_sentiment.count(-1)))

b_bot_invol_issues_sentiment = transfer_to_score(b_bot_invol_issues_sentiment)
print('b_bot_invol_issues_sentiment:')
print('positive:' + str(b_bot_invol_issues_sentiment.count(1)))
print('neutral:' + str(b_bot_invol_issues_sentiment.count(0)))
print('negative:' + str(b_bot_invol_issues_sentiment.count(-1)))
b_bot_invol_pulls_sentiment = transfer_to_score(b_bot_invol_pulls_sentiment)
print('b_bot_invol_pulls_sentiment:')
print('positive:' + str(b_bot_invol_pulls_sentiment.count(1)))
print('neutral:' + str(b_bot_invol_pulls_sentiment.count(0)))
print('negative:' + str(b_bot_invol_pulls_sentiment.count(-1)))
a_bot_invol_issues_sentiment = transfer_to_score(a_bot_invol_issues_sentiment)
print('a_bot_invol_issues_sentiment:')
print('positive:' + str(a_bot_invol_issues_sentiment.count(1)))
print('neutral:' + str(a_bot_invol_issues_sentiment.count(0)))
print('negative:' + str(a_bot_invol_issues_sentiment.count(-1)))
a_bot_invol_pulls_sentiment = transfer_to_score(a_bot_invol_pulls_sentiment)
print('a_bot_invol_pulls_sentiment:')
print('positive:' + str(a_bot_invol_pulls_sentiment.count(1)))
print('neutral:' + str(a_bot_invol_pulls_sentiment.count(0)))
print('negative:' + str(a_bot_invol_pulls_sentiment.count(-1)))

p1 = get_p_value(bot_created_issues_sentiment, human_created_issues_sentiment)
p2 = get_p_value(bot_created_pulls_sentiment, human_created_pulls_sentiment)
p3 = get_p_value(bot_invol_issues_sentiment, wo_bot_invol_issues_sentiment)
p4 = get_p_value(bot_invol_pulls_sentiment, wo_bot_invol_pulls_sentiment)
p5 = get_p_value(b_bot_invol_issues_sentiment, a_bot_invol_issues_sentiment)
p6 = get_p_value(b_bot_invol_pulls_sentiment, a_bot_invol_pulls_sentiment)

print("bot/human create issues p-value:" + str(p1))
print("bot/human create pulls p-value:" + str(p2))
print("bot invol/wo_invol issues p-value:" + str(p3))
print("bot invol/wo_invol pulls p-value:" + str(p4))
print("before/after bot invol issues p-value:" + str(p5))
print("before/after bot invol pulls p-value:" + str(p6))