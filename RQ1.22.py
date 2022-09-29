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
    sql_query = "SELECT DISTINCT owner, repo_name, commenter, event_type, event_number, sentiment FROM issue_comment WHERE owner = %(repo_owner)s AND repo_name = %(repo_name)s ORDER BY event_number ASC, updated_at ASC"
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

def update_sentiment(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "UPDATE repo_info_data SET b_bot_issue_sentiment = (%s), a_bot_issue_sentiment = (%s), b_bot_pr_sentiment = (%s), a_bot_pr_sentiment = (%s) WHERE owner = (%s) AND repo_name = (%s)"
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

for repo in repo_info:
    comment_list = get_comments_info(repo[0], repo[1])
    issue_has_bot_list = []
    pr_has_bot_list = []
    for comment in comment_list:
        if comment[2] in bot_list and comment[3] == 'issues':
            issue_has_bot_list.append(comment[4])
        if comment[2] in bot_list and comment[3] == 'pull':
            pr_has_bot_list.append(comment[4])

    issue_has_bot_list = list(set(issue_has_bot_list))
    pr_has_bot_list = list(set(pr_has_bot_list))
    number_temp = comment_list[0][4]
    b_bot_issue_sentiment = []
    a_bot_issue_sentiment = []
    b_bot_pr_sentiment = []
    a_bot_pr_sentiment = []
    bot_flag = 0
    for comment in comment_list:
        if comment[4] != number_temp:
            number_temp = comment[4]
            bot_flag = 0
            if comment[4] not in issue_has_bot_list and comment[4] not in pr_has_bot_list:
                continue
            if comment[4] in issue_has_bot_list:
                if comment[2] in bot_list:
                    bot_flag = 1
                if comment[2] not in bot_list and bot_flag == 0:
                    b_bot_issue_sentiment.append(comment[5])
                if comment[2] not in bot_list and bot_flag == 1:
                    a_bot_issue_sentiment.append(comment[5])

            if comment[4] in pr_has_bot_list:
                if comment[2] in bot_list:
                    bot_flag = 1
                if comment[2] not in bot_list and bot_flag == 0:
                    b_bot_pr_sentiment.append(comment[5])
                if comment[2] not in bot_list and bot_flag == 1:
                    a_bot_pr_sentiment.append(comment[5])

        elif comment[4] == number_temp:
            if comment[4] not in issue_has_bot_list and comment[4] not in pr_has_bot_list:
                continue
            if comment[4] in issue_has_bot_list:
                if comment[2] in bot_list:
                    bot_flag = 1
                if comment[2] not in bot_list and bot_flag == 0:
                    b_bot_issue_sentiment.append(comment[5])
                if comment[2] not in bot_list and bot_flag == 1:
                    a_bot_issue_sentiment.append(comment[5])

            if comment[4] in pr_has_bot_list:
                if comment[2] in bot_list:
                    bot_flag = 1
                if comment[2] not in bot_list and bot_flag == 0:
                    b_bot_pr_sentiment.append(comment[5])
                if comment[2] not in bot_list and bot_flag == 1:
                    a_bot_pr_sentiment.append(comment[5])

    b_bot_issue_sentiment = transfer_to_score(b_bot_issue_sentiment)
    a_bot_issue_sentiment = transfer_to_score(a_bot_issue_sentiment)
    b_bot_pr_sentiment = transfer_to_score(b_bot_pr_sentiment)
    a_bot_pr_sentiment = transfer_to_score(a_bot_pr_sentiment)

    b_bot_issue_score = (b_bot_issue_sentiment.count(1) - b_bot_issue_sentiment.count(-1)) / len(b_bot_issue_sentiment) if len(b_bot_issue_sentiment) > 0 else None
    a_bot_issue_score = (a_bot_issue_sentiment.count(1) - a_bot_issue_sentiment.count(-1)) / len(a_bot_issue_sentiment) if len(a_bot_issue_sentiment) > 0 else None
    b_bot_pr_score = (b_bot_pr_sentiment.count(1) - b_bot_pr_sentiment.count(-1)) / len(b_bot_pr_sentiment) if len(b_bot_pr_sentiment) > 0 else None
    a_bot_pr_score = (a_bot_pr_sentiment.count(1) - a_bot_pr_sentiment.count(-1)) / len(a_bot_pr_sentiment) if len(a_bot_pr_sentiment) > 0 else None
    update_sentiment([b_bot_issue_score, a_bot_issue_score, b_bot_pr_score, a_bot_pr_score, repo[0], repo[1]])

    print(b_bot_issue_score)
    print(a_bot_issue_score)
    print(b_bot_pr_score)
    print(a_bot_pr_score)
    print(repo[0] + "/" + repo[1] + " : success!")