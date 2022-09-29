import pymysql
from collections import Counter

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
    sql_query = "SELECT DISTINCT owner, repo_name, commenter, sentiment FROM issue_comment WHERE owner = %(repo_owner)s AND repo_name = %(repo_name)s"
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

def update_has_bot(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "UPDATE repo_info_data SET has_bot = (%s), positive = (%s), neutral = (%s), negative = (%s) WHERE owner = (%s) AND repo_name = (%s)"
    try:
        # 执行SQL语句
        cursor.execute(sql_query, value)
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("update_repo_info error:")
        print(e)

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

repo_info = get_repos_info()
bot_list = [x[0] for x in get_bots_info()]
total_bot_list = []

for repo in repo_info:
    comment_info = get_comments_info(repo[0], repo[1])
    bot_list_temp = []
    sentiment_list_temp = []
    for comment in comment_info:
        if comment[2] in bot_list and comment[2] not in bot_list_temp:
            bot_list_temp.append(comment[2])

    for bot in bot_list_temp:
        total_bot_list.append(bot)

    """for comment in comment_info:
        if comment[2] not in bot_list:
            sentiment_list_temp.append(comment[3])"""

    """sentiment_list_temp = transfer_to_score(sentiment_list_temp)
    update_has_bot([len(bot_list_temp), sentiment_list_temp.count(1), sentiment_list_temp.count(0), sentiment_list_temp.count(-1), comment[0], comment[1]])"""
    print(bot_list_temp)
    print(repo[0] + "/" + repo[1] + " : success!")

collection_words = Counter(total_bot_list)
print(collection_words)
total_bot_list = collection_words.most_common(10)

"""has_bot_sentiment = []
has_no_bot_sentiment = []

for comment in comment_info:
    if comment[0] + "/" + comment[1] in has_bot_repo and comment[2] not in bot_list:
        has_bot_sentiment.append(comment[3])
    elif comment[0] + "/" + comment[1] not in has_bot_repo:
        has_no_bot_sentiment.append(comment[3])

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

has_bot_sentiment = transfer_to_score(has_bot_sentiment)
print('has_bot_sentiment:')
print('positive:' + str(has_bot_sentiment.count(1)))
print('neutral:' + str(has_bot_sentiment.count(0)))
print('negative:' + str(has_bot_sentiment.count(-1)))
has_no_bot_sentiment = transfer_to_score(has_no_bot_sentiment)
print('has_no_bot_sentiment:')
print('positive:' + str(has_no_bot_sentiment.count(1)))
print('neutral:' + str(has_no_bot_sentiment.count(0)))
print('negative:' + str(has_no_bot_sentiment.count(-1)))"""