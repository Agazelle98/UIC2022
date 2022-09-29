import pymysql
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
    sql_query = "SELECT DISTINCT owner, repo_name, commenter, comment, sentiment FROM issue_comment WHERE owner = %(repo_owner)s AND repo_name = %(repo_name)s ORDER BY updated_at ASC"
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

def get_at_bot_comments_info(owner, repo_name, bot_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    #INSERT INTO comment_at_bot (comment_id, url, commenter, comment, sentiment)
    sql_query = "SELECT DISTINCT comment_id, url, commenter, comment, sentiment FROM issue_comment WHERE owner = '" + owner + "' AND repo_name = '" + repo_name + "' AND comment LIKE '%@" + bot_name + "%' AND commenter NOT IN (SELECT bot_name FROM bot_info_data) AND (sentiment = 'positive' OR sentiment = 'negative')"
    #values = {"repo_owner": owner, "repo_name": repo_name}
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

def insert_into_comment_at_bot(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "INSERT INTO comment_at_bot(comment_id, url, commenter, comment, sentiment, bot_name) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        # 执行SQL语句
        cursor.execute(sql_query, value)
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("insert_pr error:")
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

for repo in repo_info:
    comment_list =  get_comments_info(repo[0], repo[1])
    repo_bot_list = []
    for comment in comment_list:
        if comment[2] in bot_list and comment[2] not in repo_bot_list:
            repo_bot_list.append(comment[2])

    repo_bot_list = list(set(repo_bot_list))
    for bot in repo_bot_list:
        bot_name = bot.replace('[bot]', '')
        comments = get_at_bot_comments_info(repo[0], repo[1], bot_name)
        for comment in comments:
            insert_into_comment_at_bot([comment[0], comment[1], comment[2], comment[3], comment[4], bot])

    print(repo[0] + "/" + repo[1] + " : success!")