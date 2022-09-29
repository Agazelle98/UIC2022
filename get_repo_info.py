import requests
import pymysql
import datetime

def str_to_datetime(str):
    #return str.split('T')[0] + ' ' + str.split('T')[1].split('Z')[0]
    return datetime.datetime.strptime(str.split('T')[0] + ' ' + str.split('T')[1].split('Z')[0], "%Y-%m-%d %H:%M:%S")

def list2str(list):
    tmp = ''
    for i in range(len(list)):
        tmp = tmp + str(list[i]) + '/'
    return tmp

def get_repos_list():
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='github_data',
                         use_unicode=True,
                         charset='utf8mb4')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql_query = "SELECT repo_owner, repo_name FROM issue_info GROUP BY repo_name"
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

def search_repo(page,owner,repo_name):
    url = 'https://api.github.com/search/repositories'
    print(url)
    # 'Accept': 'application/vnd.github.cloak-preview'
    headers = {'User-Agent': 'Mozilla/5.0',
               'Authorization': 'token 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',
               'Content-Type': 'application/json',
               'Accept': 'application/json'
               }
    params = {'sort': 'stars',
              'page': page,
              'per_page': 100,
              'order': 'desc',
              'q': "repo:" + owner + "/" + repo_name
              #'q': "stars:>=5000 forks:>=5000 size:>=10000 pushed:>=2022-01-01"
              #'q': "stars:" + str(low) + ".." + str(high)
              }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(response.json())
        print('get_repo error: fail to request')
    j = response.json()
    for repo in j['items']:
        if repo['fork'] == False and repo['private'] == False:
            value = [repo['id'], repo['name'], repo['owner']['login'], repo['owner']['type'], str_to_datetime(str(repo['created_at'])),
                     str_to_datetime(str(repo['updated_at'])), repo['description'], list2str(repo['topics'])[:-1], repo['forks_count'],
                     repo['watchers_count'], repo['stargazers_count'], repo['size'], repo['html_url'], repo['issues_url'],
                     repo['pulls_url'], repo['comments_url']]
            save_repos_info(value)
            #print(value)
            print(str(repo['id']) + repo['name'])
    return len(j['items'])

def save_repos_info(value):
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
    sql = """INSERT INTO repo_info_data(repo_id,repo_name,owner,user_type,created_at,updated_at,description,topics,
             forks_count,watchers_count,stars,size,html_url,issues_url,pulls_url,comments_url) VALUES (%s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # 使用 execute()  方法执行 SQL 查询
    try:
        # 执行sql语句
        cursor.execute(sql, value)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        print("ERR0R:")
        print(e)
    # 关闭数据库连接
    db.close()

if __name__ == '__main__':
    repo_list = [[x[0], x[1]] for x in get_repos_list()]
    repo_list_crawled = [[x[0], x[1]] for x in get_repos_info()]
    new_repo_list = []
    for repo in repo_list:
        if repo not in repo_list_crawled:
            new_repo_list.append(repo)

    for repo in new_repo_list:
        cnt = search_repo(1,repo[0],repo[1])
        if cnt == 0:
            break