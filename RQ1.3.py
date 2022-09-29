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
    sql_query = "SELECT owner, repo_name FROM repo_info_data WHERE has_bot > '0' AND id > '25'"
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
    sql_query = "SELECT DISTINCT commenter, event_number, sentiment FROM issue_comment WHERE owner = %(repo_owner)s AND repo_name = %(repo_name)s ORDER BY event_number ASC, updated_at ASC"
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
    sql_query = "SELECT issue_type, issue_number, issue_proposer FROM issue_info WHERE repo_owner = %(repo_owner)s AND repo_name = %(repo_name)s AND comments_count > '0'"
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

def update_sentiment(value):
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "UPDATE repo_info_data SET bot_propose_issue_sentiment = (%s), human_propose_issue_sentiment = (%s), bot_propose_pr_sentiment = (%s), human_propose_pr_sentiment = (%s) WHERE owner = (%s) AND repo_name = (%s)"
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
    issue_list = get_issues_info(repo[0], repo[1])
    bot_propose_issue = []
    human_propose_issue = []
    bot_propose_pr = []
    human_propose_pr = []
    for issue in issue_list:
        if issue[0] == 'issues' and issue[2] in bot_list:
            bot_propose_issue.append(issue[1])
        if issue[0] == 'issues' and issue[2] not in bot_list:
            human_propose_issue.append(issue[1])
        if issue[0] == 'pull' and issue[2] in bot_list:
            bot_propose_pr.append(issue[1])
        if issue[0] == 'pull' and issue[2] not in bot_list:
            human_propose_pr.append(issue[1])

    bot_propose_issue_sentiment = []
    human_propose_issue_sentiment= []
    bot_propose_pr_sentiment = []
    human_propose_pr_sentiment = []

    for comment in comment_list:
        if comment[1] in bot_propose_issue and comment[0] not in bot_list:
            bot_propose_issue_sentiment.append(comment[2])
        if comment[1] in human_propose_issue and comment[0] not in bot_list:
            human_propose_issue_sentiment.append(comment[2])
        if comment[1] in bot_propose_pr and comment[0] not in bot_list:
            bot_propose_pr_sentiment.append(comment[2])
        if comment[1] in human_propose_pr and comment[0] not in bot_list:
            human_propose_pr_sentiment.append(comment[2])

    bot_propose_issue_sentiment = transfer_to_score(bot_propose_issue_sentiment)
    human_propose_issue_sentiment = transfer_to_score(human_propose_issue_sentiment)
    bot_propose_pr_sentiment = transfer_to_score(bot_propose_pr_sentiment)
    human_propose_pr_sentiment = transfer_to_score(human_propose_pr_sentiment)

    bot_propose_issue_score = (bot_propose_issue_sentiment.count(1) - bot_propose_issue_sentiment.count(-1)) / len(bot_propose_issue_sentiment) if len(bot_propose_issue_sentiment) > 0 else None
    human_propose_issue_score = (human_propose_issue_sentiment.count(1) - human_propose_issue_sentiment.count(-1)) / len(human_propose_issue_sentiment) if len(human_propose_issue_sentiment) > 0 else None
    bot_propose_pr_score = (bot_propose_pr_sentiment.count(1) - bot_propose_pr_sentiment.count(-1)) / len(bot_propose_pr_sentiment) if len(bot_propose_pr_sentiment) > 0 else None
    human_propose_pr_score = (human_propose_pr_sentiment.count(1) - human_propose_pr_sentiment.count(-1)) / len(human_propose_pr_sentiment) if len(human_propose_pr_sentiment) > 0 else None

    print(bot_propose_issue_score)
    print(human_propose_issue_score)
    print(bot_propose_pr_score)
    print(human_propose_pr_score)
    update_sentiment([bot_propose_issue_score, human_propose_issue_score, bot_propose_pr_score, human_propose_pr_score, repo[0], repo[1]])

    print(repo[0] + "/" + repo[1] + " : success!")
