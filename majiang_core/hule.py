import re
from .shan import Shan
from .shoupai import Shoupai
import math

def hule(shoupai:Shoupai, rongpai:str, param):
    if rongpai:
        if not rongpai[-1] in ['+', '=', '-']:
            raise ValueError(rongpai)
        rongpai = rongpai[:2] + rongpai[-1]

    max_result = None

    pre_hupai = get_pre_hupai(param['hupai'])
    post_hupai = get_post_hupai(shoupai, rongpai, param['baopai'], param['fubaopai'])

    for mianzi in hule_mianzi(shoupai, rongpai):
        hudi = get_hudi(mianzi, param['zhuangfeng'], param['menfeng'], param['rule'])
        hupai = get_hupai(mianzi, hudi, pre_hupai, post_hupai, param['rule'])
        rv = get_defen(hudi['fu'], hupai, rongpai, param)

        if (max_result is None or 
            rv['defen'] > max_result['defen'] or
            (rv['defen'] == max_result['defen'] and
             (not rv.get('fanshu') or
              rv['fanshu'] > max_result['fanshu'] or
              (rv['fanshu'] == max_result['fanshu'] and rv['fu'] > max_result['fu'])))):
            max_result = rv

    return max_result

def get_pre_hupai(hupai):
    pre_hupai = []

    if hupai.get('lizhi') == 1:
        pre_hupai.append({'name': '立直', 'fanshu': 1})
    if hupai.get('lizhi') == 2:
        pre_hupai.append({'name': 'ダブル立直', 'fanshu': 2})
    if hupai.get('yifa'):
        pre_hupai.append({'name': '一発', 'fanshu': 1})
    if hupai.get('haidi') == 1:
        pre_hupai.append({'name': '海底摸月', 'fanshu': 1})
    if hupai.get('haidi') == 2:
        pre_hupai.append({'name': '河底撈魚', 'fanshu': 1})
    if hupai.get('lingshang'):
        pre_hupai.append({'name': '嶺上開花', 'fanshu': 1})
    if hupai.get('qianggang'):
        pre_hupai.append({'name': '槍槓', 'fanshu': 1})

    if hupai.get('tianhu') == 1:
        pre_hupai = [{'name': '天和', 'fanshu': '*'}]
    if hupai.get('tianhu') == 2:
        pre_hupai = [{'name': '地和', 'fanshu': '*'}]

    return pre_hupai

def get_post_hupai(shoupai:Shoupai, rongpai:str, baopai, fubaopai):
    new_shoupai = shoupai.clone()
    if rongpai:
        new_shoupai.zimo(rongpai)
    paistr = new_shoupai.to_string()

    post_hupai = []

    suitstr = re.findall(r'[mpsz][^mpsz,]*', paistr)

    n_baopai = 0
    for p in baopai:
        p = Shan.zhenbaopai(p)
        regexp = re.compile(p[1])
        for m in suitstr:
            if m[0] != p[0]:
                continue
            m = m.replace('0', '5')
            nn = regexp.findall(m)
            if nn:
                n_baopai += len(nn)
    if n_baopai:
        post_hupai.append({'name': 'ドラ', 'fanshu': n_baopai})

    n_hongpai = paistr.count('0')
    if n_hongpai:
        post_hupai.append({'name': '赤ドラ', 'fanshu': n_hongpai})

    n_fubaopai = 0
    for p in (fubaopai or []):
        p = Shan.zhenbaopai(p)
        regexp = re.compile(p[1])
        for m in suitstr:
            if m[0] != p[0]:
                continue
            m = m.replace('0', '5')
            nn = regexp.findall(m)
            if nn:
                n_fubaopai += len(nn)
    if n_fubaopai:
        post_hupai.append({'name': '裏ドラ', 'fanshu': n_fubaopai})

    return post_hupai

def hule_mianzi_yiban(shoupai:Shoupai, hulepai:str):
    mianzi = []
    for s in ['m', 'p', 's', 'z']:
        bingpai = shoupai.bingpai[s]
        for n in range(1, len(bingpai)):
            if bingpai[n] < 2:
                continue
            bingpai[n] -= 2
            jiangpai = s + str(n) + str(n)
            for mm in mianzi_all(shoupai):
                mm.insert(0, jiangpai)
                if len(mm) != 5:
                    continue
                mianzi.extend(add_hulepai(mm, hulepai))
            bingpai[n] += 2
    return mianzi

def get_hudi(mianzi, zhuangfeng, menfeng, rule):
    zhuangfengpai = re.compile(f'^z{zhuangfeng + 1}.*$')
    menfengpai = re.compile(f'^z{menfeng + 1}.*$')
    sanyuanpai = re.compile(r'^z[567].*$')
    yaojiu = re.compile(r'^.*[z19].*$')
    zipai = re.compile(r'^z.*$')
    kezi = re.compile(r'^[mpsz](\d)\1\1.*$')
    ankezi = re.compile(r'^[mpsz](\d)\1\1(?:\1|_\!)?$')
    gangzi = re.compile(r'^[mpsz](\d)\1\1.*\1.*$')
    danqi = re.compile(r'^[mpsz](\d)\1[\+\=\-\_]\!$')
    kanzhang = re.compile(r'^[mps]\d\d[\+\=\-\_]\!\d$')
    bianzhang = re.compile(r'^[mps](123[\+\=\-\_]\!|7[\+\=\-\_]\!89)$')

    hudi = {
        'fu': 20,
        'menqian': True,
        'zimo': True,
        'shunzi': {
            'm': [0] * 8,
            'p': [0] * 8,
            's': [0] * 8
        },
        'kezi': {
            'm': [0] * 10,
            'p': [0] * 10,
            's': [0] * 10,
            'z': [0] * 8
        },
        'n_shunzi': 0,
        'n_kezi': 0,
        'n_ankezi': 0,
        'n_gangzi': 0,
        'n_yaojiu': 0,
        'n_zipai': 0,
        'danqi': False,
        'pinghu': False,
        'zhuangfeng': zhuangfeng,
        'menfeng': menfeng
    }

    for m in mianzi:
        if re.search(r'[\+\=\-](?!\!)', m):
            hudi['menqian'] = False
        if re.search(r'[\+\=\-]\!', m):
            hudi['zimo'] = False
        if len(mianzi) == 1:
            continue
        if danqi.match(m):
            hudi['danqi'] = True
        if len(mianzi) == 13:
            continue
        if yaojiu.match(m):
            hudi['n_yaojiu'] += 1
        if zipai.match(m):
            hudi['n_zipai'] += 1
        if len(mianzi) != 5:
            continue
        if m == mianzi[0]:
            fu = 0
            if zhuangfengpai.match(m):
                fu += 2
            if menfengpai.match(m):
                fu += 2
            if sanyuanpai.match(m):
                fu += 2
            fu = 2 if rule['連風牌は2符'] and fu > 2 else fu
            hudi['fu'] += fu
            if hudi['danqi']:
                hudi['fu'] += 2
        elif kezi.match(m):
            hudi['n_kezi'] += 1
            fu = 2
            if yaojiu.match(m):
                fu *= 2
            if ankezi.match(m):
                fu *= 2
                hudi['n_ankezi'] += 1
            if gangzi.match(m):
                fu *= 4
                hudi['n_gangzi'] += 1
            hudi['fu'] += fu
            a = m[0]
            b = int(m[1])
            hudi['kezi'][a][b] += 1
        else:
            hudi['n_shunzi'] += 1
            if kanzhang.match(m):
                hudi['fu'] += 2
            if bianzhang.match(m):
                hudi['fu'] += 2
            a = m[0]
            b = int(m[1])
            hudi['shunzi'][a][b] += 1

    if len(mianzi) == 7:
        hudi['fu'] = 25
    elif len(mianzi) == 5:
        hudi['pinghu'] = hudi['menqian'] and hudi['fu'] == 20
        if hudi['zimo']:
            if not hudi['pinghu']:
                hudi['fu'] += 2
        else:
            if hudi['menqian']:
                hudi['fu'] += 10
            elif hudi['fu'] == 20:
                hudi['fu'] = 30
        hudi['fu'] = math.ceil(hudi['fu'] / 10) * 10

    return hudi


def get_hupai(mianzi, hudi, pre_hupai, post_hupai, rule):
    def menqianqing():
        if hudi['menqian'] and hudi['zimo']:
            return [{'name': '門前清自摸和', 'fanshu': 1}]
        return []

    def fanpai():
        feng_hanzi = ['東', '南', '西', '北']
        fanpai_all = []
        if hudi['kezi']['z'][hudi['zhuangfeng'] + 1]:
            fanpai_all.append({
                'name': f"場風 {feng_hanzi[hudi['zhuangfeng']]}",
                'fanshu': 1
            })
        if hudi['kezi']['z'][hudi['menfeng'] + 1]:
            fanpai_all.append({
                'name': f"自風 {feng_hanzi[hudi['menfeng']]}",
                'fanshu': 1
            })
        if hudi['kezi']['z'][5]:
            fanpai_all.append({'name': '翻牌 白', 'fanshu': 1})
        if hudi['kezi']['z'][6]:
            fanpai_all.append({'name': '翻牌 發', 'fanshu': 1})
        if hudi['kezi']['z'][7]:
            fanpai_all.append({'name': '翻牌 中', 'fanshu': 1})
        return fanpai_all

    def pinghu():
        if hudi['pinghu']:
            return [{'name': '平和', 'fanshu': 1}]
        return []

    def duanyaojiu():
        if hudi['n_yaojiu'] > 0:
            return []
        if rule['クイタンあり'] or hudi['menqian']:
            return [{'name': '断幺九', 'fanshu': 1}]
        return []

    def yibeikou():
        if not hudi['menqian']:
            return []
        shunzi = hudi['shunzi']
        beikou = sum(x >> 1 for x in shunzi['m'] + shunzi['p'] + shunzi['s'])
        if beikou == 1:
            return [{'name': '一盃口', 'fanshu': 1}]
        return []

    def sansetongshun():
        shunzi = hudi['shunzi']
        for n in range(1, 8):
            if shunzi['m'][n] and shunzi['p'][n] and shunzi['s'][n]:
                return [{'name': '三色同順', 'fanshu': 2 if hudi['menqian'] else 1}]
        return []

    def yiqitongguan():
        shunzi = hudi['shunzi']
        for s in ['m', 'p', 's']:
            if shunzi[s][1] and shunzi[s][4] and shunzi[s][7]:
                return [{'name': '一気通貫', 'fanshu': 2 if hudi['menqian'] else 1}]
        return []

    def hunquandaiyaojiu():
        if hudi['n_yaojiu'] == 5 and hudi['n_shunzi'] > 0 and hudi['n_zipai'] > 0:
            return [{'name': '混全帯幺九', 'fanshu': 2 if hudi['menqian'] else 1}]
        return []

    def qiduizi():
        if len(mianzi) == 7:
            return [{'name': '七対子', 'fanshu': 2}]
        return []

    def duiduihu():
        if hudi['n_kezi'] == 4:
            return [{'name': '対々和', 'fanshu': 2}]
        return []

    def sananke():
        if hudi['n_ankezi'] == 3:
            return [{'name': '三暗刻', 'fanshu': 2}]
        return []

    def sangangzi():
        if hudi['n_gangzi'] == 3:
            return [{'name': '三槓子', 'fanshu': 2}]
        return []

    def sansetongke():
        kezi = hudi['kezi']
        for n in range(1, 10):
            if kezi['m'][n] and kezi['p'][n] and kezi['s'][n]:
                return [{'name': '三色同刻', 'fanshu': 2}]
        return []

    def hunlaotou():
        if hudi['n_yaojiu'] == len(mianzi) and hudi['n_shunzi'] == 0 and hudi['n_zipai'] > 0:
            return [{'name': '混老頭', 'fanshu': 2}]
        return []

    def xiaosanyuan():
        kezi = hudi['kezi']
        if kezi['z'][5] + kezi['z'][6] + kezi['z'][7] == 2 and re.match(r'^z[567]', mianzi[0]):
            return [{'name': '小三元', 'fanshu': 2}]
        return []

    def hunyise():
        for s in ['m', 'p', 's']:
            yise = re.compile(f'^[z{s}]')
            if len([m for m in mianzi if yise.match(m)]) == len(mianzi) and hudi['n_zipai'] > 0:
                return [{'name': '混一色', 'fanshu': 3 if hudi['menqian'] else 2}]
        return []

    def chunquandaiyaojiu():
        if hudi['n_yaojiu'] == 5 and hudi['n_shunzi'] > 0 and hudi['n_zipai'] == 0:
            return [{'name': '純全帯幺九', 'fanshu': 3 if hudi['menqian'] else 2}]
        return []

    def erbeikou():
        if not hudi['menqian']:
            return []
        shunzi = hudi['shunzi']
        beikou = sum(x >> 1 for x in shunzi['m'] + shunzi['p'] + shunzi['s'])
        if beikou == 2:
            return [{'name': '二盃口', 'fanshu': 3}]
        return []

    def qingyise():
        for s in ['m', 'p', 's']:
            yise = re.compile(f'^[{s}]')
            if len([m for m in mianzi if yise.match(m)]) == len(mianzi):
                return [{'name': '清一色', 'fanshu': 6 if hudi['menqian'] else 5}]
        return []

    def guoshiwushuang():
        if len(mianzi) != 13:
            return []
        if hudi['danqi']:
            return [{'name': '国士無双十三面', 'fanshu': '**'}]
        else:
            return [{'name': '国士無双', 'fanshu': '*'}]

    def sianke():
        if hudi['n_ankezi'] != 4:
            return []
        if hudi['danqi']:
            return [{'name': '四暗刻単騎', 'fanshu': '**'}]
        else:
            return [{'name': '四暗刻', 'fanshu': '*'}]

    def dasanyuan():
        kezi = hudi['kezi']
        if kezi['z'][5] + kezi['z'][6] + kezi['z'][7] == 3:
            bao_mianzi = [m for m in mianzi if re.match(r'^z([567])\1\1(?:[\+\=\-]|\1)(?!\!)', m)]
            baojia = bao_mianzi[2] and re.search(r'[\+\=\-]', bao_mianzi[2])
            if baojia:
                return [{'name': '大三元', 'fanshu': '*', 'baojia': baojia.group()}]
            else:
                return [{'name': '大三元', 'fanshu': '*'}]
        return []

    def sixihu():
        kezi = hudi['kezi']
        if kezi['z'][1] + kezi['z'][2] + kezi['z'][3] + kezi['z'][4] == 4:
            bao_mianzi = [m for m in mianzi if re.match(r'^z([1234])\1\1(?:[\+\=\-]|\1)(?!\!)', m)]
            baojia = bao_mianzi[3] and re.search(r'[\+\=\-]', bao_mianzi[3])
            if baojia:
                return [{'name': '大四喜', 'fanshu': '**', 'baojia': baojia.group()}]
            else:
                return [{'name': '大四喜', 'fanshu': '**'}]
        if kezi['z'][1] + kezi['z'][2] + kezi['z'][3] + kezi['z'][4] == 3 and re.match(r'^z[1234]', mianzi[0]):
            return [{'name': '小四喜', 'fanshu': '*'}]
        return []

    def ziyise():
        if hudi['n_zipai'] == len(mianzi):
            return [{'name': '字一色', 'fanshu': '*'}]
        return []

    def lvyise():
        if any(re.match(r'^[mp]', m) for m in mianzi):
            return []
        if any(re.match(r'^z[^6]', m) for m in mianzi):
            return []
        if any(re.match(r'^s.*[1579]', m) for m in mianzi):
            return []
        return [{'name': '緑一色', 'fanshu': '*'}]

    def qinglaotou():
        if hudi['n_yaojiu'] == 5 and hudi['n_kezi'] == 4 and hudi['n_zipai'] == 0:
            return [{'name': '清老頭', 'fanshu': '*'}]
        return []

    def sigangzi():
        if hudi['n_gangzi'] == 4:
            return [{'name': '四槓子', 'fanshu': '*'}]
        return []

    def jiulianbaodeng():
        if len(mianzi) != 1:
            return []
        if re.match(r'^[mpsz]1112345678999', mianzi[0]):
            return [{'name': '純正九蓮宝燈', 'fanshu': '**'}]
        else:
            return [{'name': '九蓮宝燈', 'fanshu': '*'}]

    damanguan = pre_hupai if pre_hupai and pre_hupai[0]['fanshu'][0] == '*' else []
    damanguan = damanguan + guoshiwushuang() + sianke() + dasanyuan() + sixihu() + ziyise() + lvyise() + qinglaotou() + sigangzi() + jiulianbaodeng()

    for hupai in damanguan:
        if not rule['ダブル役満あり']:
            hupai['fanshu'] = '*'
        if not rule['役満パオあり']:
            hupai.pop('baojia', None)

    if damanguan:
        return damanguan

    hupai = pre_hupai + menqianqing() + fanpai() + pinghu() + duanyaojiu() + yibeikou() + sansetongshun() + yiqitongguan() + hunquandaiyaojiu() + qiduizi() + duiduihu() + sananke() + sangangzi() + sansetongke() + hunlaotou() + xiaosanyuan() + hunyise() + chunquandaiyaojiu() + erbeikou() + qingyise()

    if hupai:
        hupai = hupai + post_hupai

    return hupai

def get_defen(fu, hupai, rongpai, param):
    if not hupai:
        return {'defen': 0}
    
    menfeng = param['menfeng']
    fanshu = damanguan = defen = base = baojia = defen2 = base2 = baojia2 = None
    
    if hupai[0]['fanshu'][0] == '*':
        fu = None
        damanguan = 1 if not param['rule']['役満の複合あり'] else sum(len(h['fanshu']) for h in hupai)
        base = 8000 * damanguan
        h = next((h for h in hupai if 'baojia' in h), None)
        if h:
            baojia = h['baojia']
            baojia2 = (menfeng + {'+': 1, '=': 2, '-': 3}[baojia]) % 4
            base2 = 8000 * min(len(h['fanshu']), damanguan)
    else:
        fanshu = sum(h['fanshu'] for h in hupai)
        if fanshu >= 13 and param['rule']['数え役満あり']:
            base = 8000
        elif fanshu >= 11:
            base = 6000
        elif fanshu >= 8:
            base = 4000
        elif fanshu >= 6:
            base = 3000
        elif param['rule']['切り上げ満貫あり'] and fu << (2 + fanshu) == 1920:
            base = 2000
        else:
            base = min(fu << (2 + fanshu), 2000)

    fenpei = [0, 0, 0, 0]
    chang = param['jicun']['changbang']
    lizhi = param['jicun']['lizhibang']
    
    if baojia2 is not None and base2 is not None:
        if rongpai:
            base2 = base2 / 2
        base = base - base2
        defen2 = base2 * (6 if menfeng == 0 else 4)
        fenpei[menfeng] += defen2
        fenpei[baojia2] -= defen2
    else:
        defen2 = 0

    if rongpai or base == 0:
        baojia = baojia2 if base == 0 else (menfeng + {'+': 1, '=': 2, '-': 3}[rongpai[2]]) % 4
        defen = math.ceil(base * (6 if menfeng == 0 else 4) / 100) * 100
        fenpei[menfeng] += defen + chang * 300 + lizhi * 1000
        if baojia is not None:
            fenpei[baojia] -= defen + chang * 300
    else:
        zhuangjia = math.ceil(base * 2 / 100) * 100
        sanjia = math.ceil(base / 100) * 100
        if menfeng == 0:
            defen = zhuangjia * 3
            for l in range(4):
                if l == menfeng:
                    fenpei[l] += defen + chang * 300 + lizhi * 1000
                else:
                    fenpei[l] -= zhuangjia + chang * 100
        else:
            defen = zhuangjia + sanjia * 2
            for l in range(4):
                if l == menfeng:
                    fenpei[l] += defen + chang * 300 + lizhi * 1000
                elif l == 0:
                    fenpei[l] -= zhuangjia + chang * 100
                else:
                    fenpei[l] -= sanjia + chang * 100

    return {
        'hupai': hupai,
        'fu': fu,
        'fanshu': fanshu,
        'damanguan': damanguan,
        'defen': defen + defen2,
        'fenpei': fenpei
    }

def mianzi_all(shoupai:Shoupai):
    shupai_all = [[]]
    for s in ['m', 'p', 's']:
        new_mianzi = []
        for mm in shupai_all:
            for nn in mianzi(s, shoupai.bingpai[s]):
                new_mianzi.append(mm + nn)
        shupai_all = new_mianzi
    
    zipai = []
    for n in range(1, 8):
        if shoupai.bingpai['z'][n] == 0:
            continue
        if shoupai.bingpai['z'][n] != 3:
            return []
        zipai.append('z' + str(n) * 3)
    
    fulou = [m.replace('0', '5') for m in shoupai.fulou_pai]
    
    return [shupai + zipai + fulou for shupai in shupai_all]

def mianzi(s, bingpai, n=1):
    if n > 9:
        return [[]]
    if bingpai[n] == 0:
        return mianzi(s, bingpai, n + 1)
    
    shunzi = []
    if n <= 7 and bingpai[n] > 0 and bingpai[n+1] > 0 and bingpai[n+2] > 0:
        bingpai[n] -= 1
        bingpai[n+1] -= 1
        bingpai[n+2] -= 1
        shunzi = mianzi(s, bingpai, n)
        bingpai[n] += 1
        bingpai[n+1] += 1
        bingpai[n+2] += 1
        for s_mianzi in shunzi:
            s_mianzi.insert(0, s + str(n) + str(n+1) + str(n+2))
    
    kezi = []
    if bingpai[n] == 3:
        bingpai[n] -= 3
        kezi = mianzi(s, bingpai, n + 1)
        bingpai[n] += 3
        for k_mianzi in kezi:
            k_mianzi.insert(0, s + str(n)*3)
    
    return shunzi + kezi

def add_hulepai(mianzi, p):
    s, n, d = p
    regexp = re.compile(f'^({s}.*{n})')
    replacer = f'\\1{d}!'
    new_mianzi = []
    
    for i in range(len(mianzi)):
        if re.search(r'[\+\=\-]|\d{4}', mianzi[i]):
            continue
        if i > 0 and mianzi[i] == mianzi[i - 1]:
            continue
        m = regexp.sub(replacer, mianzi[i])
        if m == mianzi[i]:
            continue
        tmp_mianzi = mianzi.copy()
        tmp_mianzi[i] = m
        new_mianzi.append(tmp_mianzi)
    
    return new_mianzi

def hule_mianzi(shoupai:Shoupai, rongpai):
    new_shoupai = shoupai.clone()
    if rongpai:
        new_shoupai.zimo(rongpai)
    if not new_shoupai.zimo_pai or len(new_shoupai.zimo_pai) > 2:
        return []
    
    hulepai = (rongpai or new_shoupai.zimo_pai + '_').replace('0', '5')
    
    hule_mianzi_yiban_result = hule_mianzi_yiban(new_shoupai, hulepai)
    hule_mianzi_qidui_result = hule_mianzi_qidui(new_shoupai, hulepai)
    hule_mianzi_guoshi_result = hule_mianzi_guoshi(new_shoupai, hulepai)
    hule_mianzi_jiulian_result = hule_mianzi_jiulian(new_shoupai, hulepai)
    
    return [
        *hule_mianzi_yiban_result,
        *hule_mianzi_qidui_result,
        *hule_mianzi_guoshi_result,
        *hule_mianzi_jiulian_result
    ]

def hule_mianzi_qidui(shoupai:Shoupai, hulepai):
    if len(shoupai.fulou_pai) > 0:
        return []
    
    mianzi = []
    for s in ['m', 'p', 's', 'z']:
        bingpai = shoupai.bingpai[s]
        for n in range(1, len(bingpai)):
            if bingpai[n] == 0:
                continue
            if bingpai[n] == 2:
                m = (s + str(n) + str(n) + hulepai[2] + '!'
                     if s + str(n) == hulepai[:2]
                     else s + str(n) + str(n))
                mianzi.append(m)
            else:
                return []
    
    return [mianzi] if len(mianzi) == 7 else []

def hule_mianzi_guoshi(shoupai:Shoupai, hulepai):
    if len(shoupai.fulou_pai) > 0:
        return []
    
    mianzi = []
    n_duizi = 0
    for s in ['m', 'p', 's', 'z']:
        bingpai = shoupai.bingpai[s]
        nn = [1, 2, 3, 4, 5, 6, 7] if s == 'z' else [1, 9]
        for n in nn:
            if bingpai[n] == 2:
                m = (s + str(n) + str(n) + hulepai[2] + '!'
                     if s + str(n) == hulepai[:2]
                     else s + str(n) + str(n))
                mianzi.insert(0, m)
                n_duizi += 1
            elif bingpai[n] == 1:
                m = (s + str(n) + hulepai[2] + '!'
                     if s + str(n) == hulepai[:2]
                     else s + str(n))
                mianzi.append(m)
            else:
                return []
    
    return [mianzi] if n_duizi == 1 else []

def hule_mianzi_jiulian(shoupai:Shoupai, hulepai):
    if len(shoupai.fulou_pai) > 0:
        return []
    
    s = hulepai[0]
    if s == 'z':
        return []
    
    mianzi = s
    bingpai = shoupai.bingpai[s]
    
    for n in range(1, 10):
        if bingpai[n] == 0:
            return []
        if (n == 1 or n == 9) and bingpai[n] < 3:
            return []
        n_pai = bingpai[n] - 1 if n == int(hulepai[1]) else bingpai[n]
        mianzi += str(n) * n_pai
    
    if len(mianzi) != 14:
        return []
    
    mianzi += hulepai[1:] + '!'
    return [[mianzi]]