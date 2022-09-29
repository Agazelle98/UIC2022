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
    sql_query = "SELECT DISTINCT owner, repo_name, commenter, updated_at, event_type, sentiment FROM issue_comment WHERE owner = %(repo_owner)s AND repo_name = %(repo_name)s ORDER BY updated_at"
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

def insert_issue_sentiment_value(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "INSERT INTO 1yearsentiment(owner,repo_name,months,issue_sentiment_score) VALUES (%s, %s, %s, %s)"
    try:
        # 执行SQL语句
        cursor.execute(sql_query, value)
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("insert_issue error:")
        print(e)

def insert_pr_sentiment_value(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "INSERT INTO 1yearsentiment(owner,repo_name,months,pr_sentiment_score) VALUES (%s, %s, %s, %s)"
    try:
        # 执行SQL语句
        cursor.execute(sql_query, value)
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print("insert_pr error:")
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
    comment_list = get_comments_info(repo[0], repo[1])
    for comment in comment_list:
        if comment[2] in bot_list:
            first_invol_time = comment[3]
            break
    month_mark = int((comment_list[0][3] - first_invol_time).days / 31)
    issue_sentiment_list = []
    pr_sentiment_list = []
    for comment in comment_list:
        if int((comment[3] - first_invol_time).days / 31) == month_mark:
            if comment[4] == 'issues' and comment[2] not in bot_list:
                issue_sentiment_list.append(comment[5])
            elif comment[4] == 'pull' and comment[2] not in bot_list:
                pr_sentiment_list.append(comment[5])
        else:
            issue_sentiment_list = transfer_to_score(issue_sentiment_list)
            pr_sentiment_list = transfer_to_score(pr_sentiment_list)
            if len(issue_sentiment_list) > 0:
                score = (issue_sentiment_list.count(1) - issue_sentiment_list.count(-1)) / len(issue_sentiment_list)
                print(score)
                issue_values = [repo[0], repo[1], month_mark, (issue_sentiment_list.count(1) - issue_sentiment_list.count(-1)) / len(issue_sentiment_list)]
                insert_issue_sentiment_value(issue_values)
                issue_sentiment_list = []
            if len(pr_sentiment_list) > 0:
                score = (pr_sentiment_list.count(1) - pr_sentiment_list.count(-1)) / len(pr_sentiment_list)
                print(score)
                pr_values = [repo[0], repo[1], month_mark, (pr_sentiment_list.count(1) - pr_sentiment_list.count(-1)) / len(pr_sentiment_list)]
                insert_pr_sentiment_value(pr_values)
                pr_sentiment_list = []
            month_mark = int((comment[3] - first_invol_time).days / 31)
            if comment[4] == 'issues':
                issue_sentiment_list.append(comment[5])
            elif comment[4] == 'pull':
                pr_sentiment_list.append(comment[5])