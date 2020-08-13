#小学春游 - 两组同学，每组1-3人，每组有一个队长;春游期间，由于景点人数较多，秩序混乱，班主任要求在指定地点，按组集合

#源数据
s = [{'name':'leader-1','belong_to':None},{'name':'jack','belong_to':'leader-2'},{'name':'lili','belong_to':'leader-1'},{'name':'leader-2','belong_to':None},{'name':'Tom', 'belong_to':'leader-1'}]
#目标数据
d = [
    {'name':'leader-1', 'team':[{'name':'lili'},{'name':'Tom'}]},
    {'name':'leader-2', 'team':[{'name':'jack'}]}
]


#小学春游 - 两组同学，每组1-3人，每组有一个队长;春游期间，由于景点人数较多，秩序混乱，班主任要求在指定地点，按组集合



def find_team(data):

    leader_data = []
    m_dict = {} # {'大哥的名字':[{'name':'lili'}]}
    for d in data:
        #{'name':xxx,'belong_to':xxxx}
        if d['belong_to']:
            # 队员
            # 判断字典中 大哥是否已经存在
            # 如果已经存在 把自己append 大哥名下 如果大哥不存在 初始化大哥
            m_dict.setdefault(d['belong_to'],[])
            m_dict[d['belong_to']].append({'name':d['name']})
        else:
            # 大哥
            leader_data.append({'name':d['name'],'team':[]})
    print(leader_data)
    # [{'name': 'leader-1', 'team': []}, {'name': 'leader-2', 'team': []}]
    print(m_dict)
    # {'leader-2': [{'name': 'jack'}], 'leader-1': [{'name': 'lili'}, {'name': 'Tom'}]}
    for l in leader_data:
        # [{'name': 'leader-1', 'team': []}
        if l['name'] in m_dict:
            l['team'] = m_dict[l['name']]

    return leader_data

print(find_team(s))
# [{'name': 'leader-1', 'team': [{'name': 'lili'}, {'name': 'Tom'}]}, {'name': 'leader-2', 'team': [{'name': 'jack'}]



