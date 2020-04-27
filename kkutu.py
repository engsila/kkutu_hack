from selenium import webdriver
import time
l=0
my_id = '' # 자신의 끄투 닉네임 적기
last_word=' '
round_tmp = []
add_word=[]
id_source=''

#크롬 설정
d = webdriver.Chrome('./chromedriver')
d.get("https://kkutu.co.kr/login/google")

#단어 파일 불러오기
f = open("no_no_kill.txt", "rt", encoding="utf-8")
word_list = [] #단어들이 들어있는 변수
for i in f:
    word_list.append(i[:-1])


#접속되었을때 user ID얻는 함수
def userId():
    global id_source
    kkutu_source = d.page_source
    id_source = kkutu_source[kkutu_source.index("UserMessage"):kkutu_source.index("UserMessage") + 16]
    if "\"" in id_source:
        id_source = id_source.split('"')[0]
        
    xpath = '//*[@id="' + id_source + '"]'
    return xpath


def now(): # 현재 첫단어 얻기
    tmp = []
    now_player_name = ' '
    while len(tmp)<2 and now_player_name!=my_id:
        rounds_current()
        tmp = d.find_elements_by_class_name('display-text')
        
        now_player = d.find_elements_by_class_name('game-user-current')
        if len(now_player) == 0:
            continue

        target = now_player[0].find_elements_by_class_name('game-user-name')
        if len(target) == 0:
            continue
            
        now_player_name = target[0].text

    if len(tmp) == 0:
        element = d.find_elements_by_class_name('jjo-display')
        result = element[0].text
    else:
        result = d.execute_script("return arguments[0].textContent", tmp[-1])
    return result


def history_word(): # 이번 라운드에서 사용한 단어 거르기
    h_w_source = d.page_source
    h_source = h_w_source.index("ellipse history-item expl-mother")
    if h_w_source.find('<label class="history-class">') != -1:
        source_end1 = h_w_source.index('<div class="history-mean ellipse">')
        source_end2 = h_w_source.index('<label class="history-class">')
        
        if source_end1 > source_end2:
            source_end = source_end2
        else:
            source_end = source_end1
    else:
        source_end = h_w_source.index('<div class="history-mean ellipse">')
        
    source_start = h_w_source.index('">', h_source, source_end)+2
    h_w = h_w_source[source_start : source_end]
    if not h_w in round_tmp:
        round_tmp.append(h_w)
        if h_w in word_list:
            word_list.remove(h_w)
        else:
            add_word.append(h_w)
            print("추가 해야할 단어들 : ", end='')
            print(add_word)

    
def rounds_current(): # 현재 라운드 확인
    global last_word
    global word_list
    global round_tmp
    global l
    round = d.find_element_by_class_name('rounds-current')
    round_word = round.text

    final_source = d.page_source
    final_source_ad = final_source.index('id="ResultDiag"')
    final_source_ad += 61
    if final_source[final_source_ad] != 'n':
        last_word = ' '
        print("게임이 끝났습니다. 단어를 추가합니다.")
        word_list+=round_tmp
        round_tmp=[]
        word_list.sort(key=lambda item: (len(item), item), reverse=True)
        l=0
        st = input() # 게임 끝나면 값 입력할 때까지 정지
        return

    if last_word != round_word:
        last_word = round_word
        print("다음 라운드가 시작됐습니다. 단어를 추가합니다.")
        word_list+=round_tmp
        round_tmp=[]
        word_list.sort(key=lambda item: (len(item), item), reverse=True)
        l=0
        

#보내기
def send(msg):
    global l
    global id_source
    UserMessage = userId()

    js = f"document.getElementById('{id_source}').value = '{msg}';"
    d.execute_script(js)

    while len(d.find_elements_by_class_name('game-user-current')) == 0:
        continue

    if l != 0:
        history_word()
    l = 1
    d.find_element_by_xpath(UserMessage).send_keys('\n')
    time.sleep(0.2)
    if not msg in round_tmp:
        round_tmp.append(msg)
    if msg in word_list:
        word_list.remove(msg)
    rounds_current()



def get_word(st): # 단어 얻기
    Two_Kill=[
    '늣', '븨', '츰', '랏', '륄', '숍', '렛', '딍', '펫', '썹', '슭', '슘',
    '킷', '듭', '훠', '얏', '믜', '츈', '껏',
    '쳔', '뀌', '죵',
    '뺌', '욘', '랙', '꾼', '윙', '션', '킨', '옳', '믄', '텬', '쳥', '첸', '즘', '섯', '싀', '램', '샅',
    '즙', '껑', '늬', '슴', '봇', '즐', '쫑', '썽', '콕', '셋', '쭝', '휼', '겅', '뭇', '듬', '켈', '늘', '믈', '뇨', '닥', '삯']
    #'념', '욱', '뢰', '혀', '율']

    tmp_word_list=[]
    for i in word_list:
        if i.startswith(st):
            for j in Two_Kill:
                if i.endswith(j):
                    return i   # 두방단어 우선탐색
            tmp_word_list.append(i)

    tmp_word_list.sort(key=lambda item: (len(item), item), reverse=True)
    return tmp_word_list[0]


#---------------------------------------------------

st = input() #시작

while True:
    start=[]
    msg = ''
    rounds_current()
    
    while len(d.find_elements_by_class_name('game-user-current')) == 0:
        continue

    start = now()
    
    if start[-1] == ')':
        tt = start
        start = []
        start.append(tt[0])
        start.append(tt[2])
    
    while True:
        msg = ''
        for st in start:
            msg = get_word(st)
            if msg != '':
                break
            
        send(msg)
        
        if len(d.find_elements_by_class_name('game-user-current')) == 0: # 상대 차례로 넘어갈 때까지 단어 찾기
            break
        else:
            round_tmp.remove(msg)
            print("삭제해야할 단어 : "+ msg)


f.close()
