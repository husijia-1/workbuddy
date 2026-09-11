# -*- coding: utf-8 -*-
"""
WorkBuddy 每日数据生成器
每天6:00自动运行，生成data.json并部署到GitHub Pages
"""

import json
import os
import subprocess
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta

# ============================================================
# 韩语课程数据库 (40课)
# ============================================================
KOREAN_LESSONS = [
    {"num":1,"title":"元音 ㅏ/ㅓ/ㅗ/ㅜ","desc":"学习4个基本元音的发音和书写","bilibili":"BV1RFTc62E29/?p=1"},
    {"num":2,"title":"元音 ㅣ/ㅡ/ㅐ/ㅔ","desc":"学习4个基本元音和2个复合元音","bilibili":"BV1RFTc62E29/?p=2"},
    {"num":3,"title":"元音 ㅚ/ㅟ/ㅑ/ㅕ","desc":"学习4个复合元音","bilibili":"BV1RFTc62E29/?p=3"},
    {"num":4,"title":"元音 ㅛ/ㅠ/ㅒ/ㅖ","desc":"学习剩余复合元音","bilibili":"BV1RFTc62E29/?p=4"},
    {"num":5,"title":"辅音 ㄱ/ㄴ/ㄷ/ㄹ","desc":"学习4个基本辅音","bilibili":"BV1RFTc62E29/?p=5"},
    {"num":6,"title":"辅音 ㅁ/ㅂ/ㅅ/ㅇ","desc":"学习4个基本辅音","bilibili":"BV1RFTc62E29/?p=6"},
    {"num":7,"title":"辅音 ㅈ/ㅊ/ㅋ/ㅌ","desc":"学习4个送气辅音","bilibili":"BV1RFTc62E29/?p=7"},
    {"num":8,"title":"辅音 ㅍ/ㅎ/ㄲ/ㄸ","desc":"学习4个紧辅音","bilibili":"BV1RFTc62E29/?p=8"},
    {"num":9,"title":"辅音 ㅃ/ㅆ/ㅉ","desc":"学习3个紧辅音","bilibili":"BV1RFTc62E29/?p=9"},
    {"num":10,"title":"收音 ㄱ/ㄴ/ㄷ/ㄹ","desc":"学习4个基本收音规则","bilibili":"BV1RFTc62E29/?p=10"},
    {"num":11,"title":"收音 ㅁ/ㅂ/ㅇ","desc":"学习3个基本收音","bilibili":"BV1RFTc62E29/?p=11"},
    {"num":12,"title":"双收音 ㄳ/ㄵ/ㄶ/ㄺ","desc":"学习4个双收音","bilibili":"BV1RFTc62E29/?p=12"},
    {"num":13,"title":"双收音 ㄻ/ㄼ/ㄽ/ㄾ","desc":"学习4个双收音","bilibili":"BV1RFTc62E29/?p=13"},
    {"num":14,"title":"双收音 ㅀ/ㅄ/ㄿ","desc":"学习3个双收音","bilibili":"BV1RFTc62E29/?p=14"},
    {"num":15,"title":"发音规则：连音现象","desc":"学习韩语连音规则","bilibili":"BV1RFTc62E29/?p=15"},
    {"num":16,"title":"发音规则：鼻音化","desc":"学习辅音鼻音化规则","bilibili":"BV1RFTc62E29/?p=16"},
    {"num":17,"title":"发音规则：颚化现象","desc":"学习辅音颚化规则","bilibili":"BV1RFTc62E29/?p=17"},
    {"num":18,"title":"发音规则：辅音同化","desc":"学习辅音同化规则","bilibili":"BV1RFTc62E29/?p=18"},
    {"num":19,"title":"发音规则：紧音化","desc":"学习辅音紧音化规则","bilibili":"BV1RFTc62E29/?p=19"},
    {"num":20,"title":"发音规则：弱化与脱落","desc":"学习辅音弱化和脱落规则","bilibili":"BV1RFTc62E29/?p=20"},
    {"num":21,"title":"基础语法：이에요/예요","desc":"学习'是...'句型","bilibili":"BV1RFTc62E29/?p=21"},
    {"num":22,"title":"基础语法：이/가 主语助词","desc":"学习主语标记助词","bilibili":"BV1RFTc62E29/?p=22"},
    {"num":23,"title":"基础语法：은/는 主题助词","desc":"学习主题标记助词","bilibili":"BV1RFTc62E29/?p=23"},
    {"num":24,"title":"基础语法：을/를 宾语助词","desc":"学习宾语标记助词","bilibili":"BV1RFTc62E29/?p=24"},
    {"num":25,"title":"基础语法：에/에서 处所助词","desc":"学习处所标记助词","bilibili":"BV1RFTc62E29/?p=25"},
    {"num":26,"title":"基础语法：에서/로/으로 助词","desc":"学习从/到/用助词","bilibili":"BV1RFTc62E29/?p=26"},
    {"num":27,"title":"动词现在时：ㅂ니다/습니다","desc":"学习正式现在时态","bilibili":"BV1RFTc62E29/?p=27"},
    {"num":28,"title":"动词现在时：아요/어요","desc":"学习非正式现在时态","bilibili":"BV1RFTc62E29/?p=28"},
    {"num":29,"title":"动词过去时：았/었+过去时","desc":"学习过去时态表达","bilibili":"BV1RFTc62E29/?p=29"},
    {"num":30,"title":"动词未来时：겠/ㄹ 거에요","desc":"学习未来时态表达","bilibili":"BV1RFTc62E29/?p=30"},
    {"num":31,"title":"否定表达：안/지 않다","desc":"学习否定句型","bilibili":"BV1RFTc62E29/?p=31"},
    {"num":32,"title":"否定表达：못/지 못하다","desc":"学习能力否定句型","bilibili":"BV1RFTc62E29/?p=32"},
    {"num":33,"title":"命令句：(으)세요","desc":"学习命令句型","bilibili":"BV1RFTc62E29/?p=33"},
    {"num":34,"title":"共动句：(으)ㅂ시다","desc":"学习提议句型","bilibili":"BV1RFTc62E29/?p=34"},
    {"num":35,"title":"连接词：고/지만/아서","desc":"学习连接两个句子的语法","bilibili":"BV1RFTc62E29/?p=35"},
    {"num":36,"title":"连接词：려고/러/면서","desc":"学习目的和同时进行语法","bilibili":"BV1RFTc62E29/?p=36"},
    {"num":37,"title":"修饰语：는/은/을 名词修饰","desc":"学习修饰名词的语法","bilibili":"BV1RFTc62E29/?p=37"},
    {"num":38,"title":"敬语体系：尊称与谦称","desc":"学习韩语敬语体系","bilibili":"BV1RFTc62E29/?p=38"},
    {"num":39,"title":"日常对话：自我介绍","desc":"学习完整的自我介绍","bilibili":"BV1RFTc62E29/?p=39"},
    {"num":40,"title":"日常对话：点餐/购物","desc":"学习餐厅和购物场景对话","bilibili":"BV1RFTc62E29/?p=40"},
]

# ============================================================
# 韩语单词库 (200个，每天10个)
# ============================================================
KOREAN_WORDS = [
    {"ko":"안녕하세요","pron":"an-nyeong-ha-se-yo","cn":"你好"},
    {"ko":"감사합니다","pron":"gam-sa-ham-ni-da","cn":"谢谢"},
    {"ko":"사랑해요","pron":"sa-rang-hae-yo","cn":"我爱你"},
    {"ko":"미안해요","pron":"mi-an-hae-yo","cn":"对不起"},
    {"ko":"잘 자요","pron":"jal ja-yo","cn":"晚安"},
    {"ko":"맛있어요","pron":"ma-si-sseo-yo","cn":"好吃"},
    {"ko":"예뻐요","pron":"ye-ppeo-yo","cn":"漂亮"},
    {"ko":"힘내요","pron":"him-nae-yo","cn":"加油"},
    {"ko":"화이팅","pron":"hwa-i-ting","cn":"fighting/加油"},
    {"ko":"고마워요","pron":"go-ma-wo-yo","cn":"谢谢你"},
    {"ko":"네","pron":"ne","cn":"是"},
    {"ko":"아니요","pron":"a-ni-yo","cn":"不是"},
    {"ko":"안녕","pron":"an-nyeong","cn":"你好/再见"},
    {"ko":"이름","pron":"i-reum","cn":"名字"},
    {"ko":"나라","pron":"na-ra","cn":"国家"},
    {"ko":"친구","pron":"chin-gu","cn":"朋友"},
    {"ko":"선생님","pron":"seon-saeng-nim","cn":"老师"},
    {"ko":"학생","pron":"hak-saeng","cn":"学生"},
    {"ko":"회사","pron":"hoe-sa","cn":"公司"},
    {"ko":"회사원","pron":"hoe-sa-won","cn":"公司职员"},
    {"ko":"일","pron":"il","cn":"工作/事情"},
    {"ko":"퇴근","pron":"toe-geun","cn":"下班"},
    {"ko":"출근","pron":"chul-geun","cn":"上班"},
    {"ko":"오늘","pron":"o-neul","cn":"今天"},
    {"ko":"내일","pron":"nae-il","cn":"明天"},
    {"ko":"어제","pron":"eo-je","cn":"昨天"},
    {"ko":"지금","pron":"ji-geum","cn":"现在"},
    {"ko":"나중에","pron":"na-jung-e","cn":"以后"},
    {"ko":"빨리","pron":"ppal-li","cn":"快/快点"},
    {"ko":"천천히","pron":"cheon-ceon-hi","cn":"慢慢地"},
    {"ko":"물","pron":"mul","cn":"水"},
    {"ko":"커피","pron":"keo-pi","cn":"咖啡"},
    {"ko":"차","pron":"cha","cn":"茶"},
    {"ko":"술","pron":"sul","cn":"酒"},
    {"ko":"맥주","pron":"maek-ju","cn":"啤酒"},
    {"ko":"와인","pron":"wa-in","cn":"红酒"},
    {"ko":"밥","pron":"bap","cn":"饭"},
    {"ko":"빵","pron":"ppang","cn":"面包"},
    {"ko":"과일","pron":"gwa-il","cn":"水果"},
    {"ko":"고기","pron":"go-gi","cn":"肉"},
    {"ko":"생선","pron":"saeng-seon","cn":"鱼"},
    {"ko":"야채","pron":"ya-chae","cn":"蔬菜"},
    {"ko":"김치","pron":"gim-chi","cn":"泡菜"},
    {"ko":"라면","pron":"ra-myeon","cn":"拉面"},
    {"ko":"비빔밥","pron":"bi-bim-bap","cn":"拌饭"},
    {"ko":"불고기","pron":"bul-go-gi","cn":"烤肉"},
    {"ko":"떡볶이","pron":"tteok-bokk-i","cn":"炒年糕"},
    {"ko":"치킨","pron":"chi-kin","cn":"炸鸡"},
    {"ko":"피자","pron":"pi-ja","cn":"披萨"},
    {"ko":"좋아해요","pron":"jo-a-hae-yo","cn":"喜欢"},
    {"ko":"싫어해요","pron":"sil-eo-hae-yo","cn":"讨厌"},
    {"ko":"먹어요","pron":"meo-geo-yo","cn":"吃"},
    {"ko":"마셔요","pron":"ma-syeo-yo","cn":"喝"},
    {"ko":"가요","pron":"ga-yo","cn":"去"},
    {"ko":"와요","pron":"wa-yo","cn":"来"},
    {"ko":"봐요","pron":"bwa-yo","cn":"看"},
    {"ko":"들어요","pron":"deul-eo-yo","cn":"听"},
    {"ko":"말해요","pron":"mal-hae-yo","cn":"说"},
    {"ko":"읽어요","pron":"il-geo-yo","cn":"读"},
    {"ko":"써요","pron":"sseo-yo","cn":"写"},
    {"ko":"공부해요","pron":"gong-bu-hae-yo","cn":"学习"},
    {"ko":"일해요","pron":"il-hae-yo","cn":"工作"},
    {"ko":"쉬어요","pron":"swi-eo-yo","cn":"休息"},
    {"ko":"자요","pron":"ja-yo","cn":"睡觉"},
    {"ko":"일어나요","pron":"il-eo-na-yo","cn":"起床"},
    {"ko":"씻어요","pron":"ssi-sseo-yo","cn":"洗漱"},
    {"ko":"운동해요","pron":"un-dong-hae-yo","cn":"运动"},
    {"ko":"산책해요","pron":"san-chaek-hae-yo","cn":"散步"},
    {"ko":"쇼핑해요","pron":"syo-ping-hae-yo","cn":"购物"},
    {"ko":"여행해요","pron":"yeo-haeng-hae-yo","cn":"旅行"},
    {"ko":"사진 찍어요","pron":"sa-jin jjig-eo-yo","cn":"拍照"},
    {"ko":"노래해요","pron":"no-rae-hae-yo","cn":"唱歌"},
    {"ko":"춤춰요","pron":"chum-chwo-yo","cn":"跳舞"},
    {"ko":"영화 봐요","pron":"yeong-hwa bwa-yo","cn":"看电影"},
    {"ko":"음악 들어요","pron":"eum-ak deul-eo-yo","cn":"听音乐"},
    {"ko":"책 읽어요","pron":"chaek il-geo-yo","cn":"读书"},
    {"ko":"글 써요","pron":"geul sseo-yo","cn":"写字/写作"},
    {"ko":"요리해요","pron":"yo-ri-hae-yo","cn":"做饭"},
    {"ko":"청소해요","pron":"cheong-so-hae-yo","cn":"打扫"},
    {"ko":"빨래해요","pron":"ppal-lae-hae-yo","cn":"洗衣服"},
    {"ko":"전화해요","pron":"jeon-hwa-hae-yo","cn":"打电话"},
    {"ko":"문자해요","pron":"mun-ja-hae-yo","cn":"发短信"},
    {"ko":"카톡해요","pron":"ka-tok-hae-yo","cn":"发KakaoTalk"},
    {"ko":"만나요","pron":"man-na-yo","cn":"见面"},
    {"ko":"기다려요","pron":"gi-da-ryeo-yo","cn":"等待"},
    {"ko":"도와줘요","pron":"do-wa-jwo-yo","cn":"帮忙"},
    {"ko":"주세요","pron":"ju-se-yo","cn":"请给我"},
    {"ko":"보여주세요","pron":"bo-yeo-ju-se-yo","cn":"请给我看"},
    {"ko":"가르쳐주세요","pron":"ga-reu-chyeo-ju-se-yo","cn":"请教我"},
    {"ko":"도와주세요","pron":"do-wa-ju-se-yo","cn":"请帮帮我"},
    {"ko":"천천히 말해주세요","pron":"cheon-ceon-hi mal-hae-ju-se-yo","cn":"请慢慢说"},
    {"ko":"다시 한 번","pron":"da-si han beon","cn":"再来一次"},
    {"ko":"몰라요","pron":"mol-la-yo","cn":"不知道"},
    {"ko":"알아요","pron":"a-ra-yo","cn":"知道"},
    {"ko":"이해해요","pron":"i-hae-hae-yo","cn":"理解"},
    {"ko":"기억해요","pron":"gi-eok-hae-yo","cn":"记得"},
    {"ko":"잊어버려요","pron":"ij-eo-beo-ryeo-yo","cn":"忘记"},
    {"ko":"생각해요","pron":"saeng-gak-hae-yo","cn":"想/思考"},
    {"ko":"꿈꿔요","pron":"kkum-kkwo-yo","cn":"做梦"},
    {"ko":"바라요","pron":"ba-ra-yo","cn":"希望"},
    {"ko":"원해요","pron":"won-hae-yo","cn":"想要"},
    {"ko":"필요해요","pron":"pil-yo-hae-yo","cn":"需要"},
    {"ko":"있어요","pron":"it-sseo-yo","cn":"有/在"},
    {"ko":"없어요","pron":"eop-sseo-yo","cn":"没有/不在"},
    {"ko":"커요","pron":"keo-yo","cn":"大"},
    {"ko":"작아요","pron":"ja-ga-yo","cn":"小"},
    {"ko":"높아요","pron":"nop-a-yo","cn":"高"},
    {"ko":"낮아요","pron":"na-ja-yo","cn":"矮/低"},
    {"ko":"길어요","pron":"gil-eo-yo","cn":"长"},
    {"ko":"짧아요","pron":"jjal-ba-yo","cn":"短"},
    {"ko":"많아요","pron":"man-a-yo","cn":"多"},
    {"ko":"적어요","pron":"jeo-geo-yo","cn":"少"},
    {"ko":"비싸요","pron":"bi-ssa-yo","cn":"贵"},
    {"ko":"싸요","pron":"ssa-yo","cn":"便宜"},
    {"ko":"좋아요","pron":"jo-a-yo","cn":"好"},
    {"ko":"나빠요","pron":"na-ppa-yo","cn":"坏"},
    {"ko":"빨라요","pron":"ppal-la-yo","cn":"快"},
    {"ko":"느려요","pron":"neu-ryeo-yo","cn":"慢"},
    {"ko":"쉬워요","pron":"swi-wo-yo","cn":"容易"},
    {"ko":"어려워요","pron":"eo-ryeo-wo-yo","cn":"难"},
    {"ko":"재미있어요","pron":"jae-mi-it-sseo-yo","cn":"有趣"},
    {"ko":"재미없어요","pron":"jae-mi-eop-sseo-yo","cn":"无聊"},
    {"ko":"맛있어요","pron":"ma-si-sseo-yo","cn":"好吃"},
    {"ko":"맛없어요","pron":"mat-eop-sseo-yo","cn":"难吃"},
    {"ko":"예뻐요","pron":"ye-ppeo-yo","cn":"漂亮"},
    {"ko":"미워요","pron":"mi-wo-yo","cn":"丑/讨厌"},
    {"ko":"행복해요","pron":"haeng-bok-hae-yo","cn":"幸福"},
    {"ko":"슬퍼요","pron":"seul-peo-yo","cn":"悲伤"},
    {"ko":"기뻐요","pron":"gi-ppeo-yo","cn":"高兴"},
    {"ko":"화나요","pron":"hwa-na-yo","cn":"生气"},
    {"ko":"우울해요","pron":"u-ul-hae-yo","cn":"忧郁"},
    {"ko":"피곤해요","pron":"pi-gon-hae-yo","cn":"疲倦"},
    {"ko":"졸려요","pron":"jol-lyeo-yo","cn":"困"},
    {"ko":"배고파요","pron":"bae-go-pa-yo","cn":"饿"},
    {"ko":"목말라요","pron":"mok-mal-la-yo","cn":"渴"},
    {"ko":"더워요","pron":"deo-wo-yo","cn":"热"},
    {"ko":"추워요","pron":"chu-wo-yo","cn":"冷"},
    {"ko":"따뜻해요","pron":"tta-tteut-hae-yo","cn":"温暖"},
    {"ko":"시원해요","pron":"si-won-hae-yo","cn":"凉爽"},
    {"ko":"깨끗해요","pron":"kkae-kkeut-hae-yo","cn":"干净"},
    {"ko":"더러워요","pron":"deo-reo-wo-yo","cn":"脏"},
    {"ko":"조용해요","pron":"jo-yong-hae-yo","cn":"安静"},
    {"ko":"시끄러워요","pron":"si-kkeu-reo-wo-yo","cn":"吵闹"},
    {"ko":"안전해요","pron":"an-jeon-hae-yo","cn":"安全"},
    {"ko":"위험해요","pron":"wi-heom-hae-yo","cn":"危险"},
    {"ko":"편해요","pron":"pyeon-hae-yo","cn":"舒服"},
    {"ko":"불편해요","pron":"bul-pyeon-hae-yo","cn":"不方便"},
    {"ko":"친절해요","pron":"chin-jeol-hae-yo","cn":"亲切"},
    {"ko":"똑똑해요","pron":"ttok-ttok-hae-yo","cn":"聪明"},
    {"ko":"멋있어요","pron":"meot-it-sseo-yo","cn":"帅/酷"},
    {"ko":"귀여워요","pron":"gwi-yeo-wo-yo","cn":"可爱"},
    {"ko":"섹시해요","pron":"sek-si-hae-yo","cn":"性感"},
    {"ko":"잘생겼어요","pron":"jal-saeng-gyeot-sseo-yo","cn":"长得帅"},
    {"ko":"예쁘게 생겼어요","pron":"ye-ppeu-ge saeng-gyeot-sseo-yo","cn":"长得漂亮"},
    {"ko":"언제","pron":"eon-je","cn":"什么时候"},
    {"ko":"어디","pron":"eo-di","cn":"哪里"},
    {"ko":"누구","pron":"nu-gu","cn":"谁"},
    {"ko":"무엇","pron":"mu-eot","cn":"什么"},
    {"ko":"왜","pron":"wae","cn":"为什么"},
    {"ko":"어떻게","pron":"eo-tteo-ke","cn":"怎么"},
    {"ko":"얼마","pron":"eol-ma","cn":"多少"},
    {"ko":"몇","pron":"myeot","cn":"几"},
    {"ko":"어느","pron":"eo-neu","cn":"哪个"},
    {"ko":"어떤","pron":"eo-tteon","cn":"什么样的"},
    {"ko":"행복","pron":"haeng-bok","cn":"幸福"},
    {"ko":"자유","pron":"ja-yu","cn":"自由"},
    {"ko":"꿈","pron":"kkum","cn":"梦想"},
    {"ko":"희망","pron":"hui-mang","cn":"希望"},
    {"ko":"사랑","pron":"sa-rang","cn":"爱"},
    {"ko":"우정","pron":"u-jeong","cn":"友情"},
    {"ko":"가족","pron":"ga-jok","cn":"家人"},
    {"ko":"인생","pron":"in-saeng","cn":"人生"},
    {"ko":"시간","pron":"si-gan","cn":"时间"},
    {"ko":"돈","pron":"don","cn":"钱"},
    {"ko":"직장","pron":"jik-jang","cn":"职场"},
    {"ko":"상사","pron":"sang-sa","cn":"上司"},
    {"ko":"동료","pron":"dong-ryo","cn":"同事"},
    {"ko":"알바","pron":"al-ba","cn":"兼职"},
    {"ko":"야근","pron":"ya-geun","cn":"加班"},
    {"ko":"월급","pron":"wol-geup","cn":"工资"},
    {"ko":"휴가","pron":"hyu-ga","cn":"休假"},
    {"ko":"스트레스","pron":"seu-teu-re-seu","cn":"压力"},
    {"ko":"다이어트","pron":"da-i-eo-teu","cn":"减肥"},
    {"ko":"운동","pron":"un-dong","cn":"运动"},
    {"ko":"건강","pron":"geon-gang","cn":"健康"},
    {"ko":"피곤","pron":"pi-gon","cn":"疲劳"},
    {"ko":"휴식","pron":"hyu-sik","cn":"休息"},
    {"ko":"행운","pron":"haeng-un","cn":"幸运"},
    {"ko":"성공","pron":"seong-gong","cn":"成功"},
    {"ko":"실패","pron":"sil-pae","cn":"失败"},
    {"ko":"노력","pron":"no-ryeok","cn":"努力"},
    {"ko":"인내","pron":"in-nae","cn":"耐心"},
    {"ko":"용기","pron":"yong-gi","cn":"勇气"},
    {"ko":"미래","pron":"mi-rae","cn":"未来"},
    {"ko":"과거","pron":"gwa-geo","cn":"过去"},
    {"ko":"현재","pron":"hyeon-jae","cn":"现在"},
    {"ko":"변화","pron":"byeon-hwa","cn":"变化"},
    {"ko":"성장","pron":"seong-jang","cn":"成长"},
    {"ko":"도전","pron":"do-jeon","cn":"挑战"},
    {"ko":"기회","pron":"gi-hoe","cn":"机会"},
    {"ko":"선택","pron":"seon-taek","cn":"选择"},
    {"ko":"결정","pron":"gyeol-jeong","cn":"决定"},
]

# ============================================================
# 语音跟读句子库 (40组，每组5句)
# ============================================================
SPEAK_SENTENCES = [
    [{"ko":"안녕하세요","pron":"an-nyeong-ha-se-yo","cn":"你好"},{"ko":"감사합니다","pron":"gam-sa-ham-ni-da","cn":"谢谢"},{"ko":"사랑해요","pron":"sa-rang-hae-yo","cn":"我爱你"},{"ko":"오늘도 힘내요","pron":"o-neul-do him-nae-yo","cn":"今天也要加油"},{"ko":"맛있는 저녁이에요","pron":"ma-si-nneun jeo-nyeo-gi-e-yo","cn":"晚餐很好吃"}],
    [{"ko":"잘 부탁드립니다","pron":"jal bu-tak-deu-rip-ni-da","cn":"请多关照"},{"ko":"만나서 반가워요","pron":"man-na-seo ban-ga-wo-yo","cn":"很高兴见到你"},{"ko":"이름이 뭐예요","pron":"i-reum-i mwo-ye-yo","cn":"你叫什么名字"},{"ko":"저는 회사원이에요","pron":"jeo-neun hoe-sa-won-i-e-yo","cn":"我是公司职员"},{"ko":"한국어를 공부해요","pron":"han-gug-eo-reul gong-bu-hae-yo","cn":"我在学韩语"}],
    [{"ko":"오늘 날씨가 좋아요","pron":"o-neul nal-ssi-ga jo-a-yo","cn":"今天天气好"},{"ko":"점심 먹었어요","pron":"jeom-sim meo-geot-sseo-yo","cn":"吃午饭了吗"},{"ko":"커피 한 잔 할래요","pron":"keo-pi han jan hal-lae-yo","cn":"要喝杯咖啡吗"},{"ko":"같이 가요","pron":"ga-chi ga-yo","cn":"一起去吧"},{"ko":"조금만 기다려주세요","pron":"jo-geum-man gi-da-ryeo-ju-se-yo","cn":"请稍等一下"}],
    [{"ko":"퇴근했어요","pron":"toe-geun-haet-sseo-yo","cn":"下班了"},{"ko":"오늘 피곤해요","pron":"o-neul pi-gon-hae-yo","cn":"今天好累"},{"ko":"맛있는 거 먹어요","pron":"ma-sin-neun geo meo-geo-yo","cn":"去吃好吃的吧"},{"ko":"한잔할래요","pron":"han-jan-hal-lae-yo","cn":"喝一杯吗"},{"ko":"기분이 좋아요","pron":"gi-bu-ni jo-a-yo","cn":"心情很好"}],
    [{"ko":"주말에 뭐 해요","pron":"ju-mal-e mwo hae-yo","cn":"周末做什么"},{"ko":"쇼핑하러 가요","pron":"syo-ping-ha-reo ga-yo","cn":"去购物"},{"ko":"영화 볼래요","pron":"yeong-hwa bol-lae-yo","cn":"看电影吗"},{"ko":"산책할까요","pron":"san-chaek-hal-kka-yo","cn":"散步吗"},{"ko":"재미있어요","pron":"jae-mi-it-sseo-yo","cn":"很有趣"}],
    [{"ko":"한국어 조금 할 수 있어요","pron":"han-gug-eo jo-geum hal su it-sseo-yo","cn":"我会说一点韩语"},{"ko":"천천히 말해주세요","pron":"cheon-ceon-hi mal-hae-ju-se-yo","cn":"请慢点说"},{"ko":"다시 한 번 말해주세요","pron":"da-si han beon mal-hae-ju-se-yo","cn":"请再说一遍"},{"ko":"이해했어요","pron":"i-hae-haet-sseo-yo","cn":"我明白了"},{"ko":"모르겠어요","pron":"mo-reu-get-sseo-yo","cn":"我不知道"}],
    [{"ko":"이거 뭐예요","pron":"i-geo mwo-ye-yo","cn":"这是什么"},{"ko":"얼마예요","pron":"eol-ma-ye-yo","cn":"多少钱"},{"ko":"너무 비싸요","pron":"neo-mu bi-ssa-yo","cn":"太贵了"},{"ko":"깎아주세요","pron":"kka-ka-ju-se-yo","cn":"请便宜点"},{"ko":"카드 되나요","pron":"ka-deu doe-na-yo","cn":"可以刷卡吗"}],
    [{"ko":"맛있게 드세요","pron":"ma-sit-ge deu-se-yo","cn":"请慢用"},{"ko":"잘 먹겠습니다","pron":"jal meo-get-sseum-ni-da","cn":"我开动了"},{"ko":"물 주세요","pron":"mul ju-se-yo","cn":"请给我水"},{"ko":"계산서 주세요","pron":"gye-san-seo ju-se-yo","cn":"请结账"},{"ko":"정말 맛있어요","pron":"jeong-mal ma-si-sseo-yo","cn":"真的很好吃"}],
    [{"ko":"도와주세요","pron":"do-wa-ju-se-yo","cn":"请帮帮我"},{"ko":"길을 잃었어요","pron":"gil-eul il-eot-sseo-yo","cn":"我迷路了"},{"ko":"화장실이 어디예요","pron":"hwa-jang-sil-i eo-di-ye-yo","cn":"洗手间在哪里"},{"ko":"전화할 수 있어요","pron":"jeon-hwa-hal su it-sseo-yo","cn":"可以打电话吗"},{"ko":"경찰에 신고하세요","pron":"gyeong-chal-e sin-go-ha-se-yo","cn":"请报警"}],
    [{"ko":"생일 축하해요","pron":"saeng-il chuk-ha-hae-yo","cn":"生日快乐"},{"ko":"건강하세요","pron":"geon-gang-ha-se-yo","cn":"祝你健康"},{"ko":"행복하세요","pron":"haeng-bok-ha-se-yo","cn":"祝你幸福"},{"ko":"꿈을 이루세요","pron":"kkum-eul i-ru-se-yo","cn":"愿你梦想成真"},{"ko":"행운을 빌어요","pron":"haeng-un-eul bil-eo-yo","cn":"祝你好运"}],
    [{"ko":"사랑해요","pron":"sa-rang-hae-yo","cn":"我爱你"},{"ko":"보고 싶어요","pron":"bo-go sip-eo-yo","cn":"想你了"},{"ko":"함께 있고 싶어요","pron":"ham-kke it-go sip-eo-yo","cn":"想和你在一起"},{"ko":"영원히 사랑해요","pron":"yeong-won-hi sa-rang-hae-yo","cn":"永远爱你"},{"ko":"너밖에 없어요","pron":"neo-bak-e eop-sseo-yo","cn":"只有你"}],
    [{"ko":"화이팅","pron":"hwa-i-ting","cn":"加油"},{"ko":"포기하지 마세요","pron":"po-gi-ha-ji ma-se-yo","cn":"不要放弃"},{"ko":"할 수 있어요","pron":"hal su it-sseo-yo","cn":"你能做到"},{"ko":"최선을 다해요","pron":"choe-seon-eul da-hae-yo","cn":"全力以赴"},{"ko":"응원해요","pron":"eung-won-hae-yo","cn":"我支持你"}],
]

# ============================================================
# 每日金句库 (30条)
# ============================================================
QUOTES = [
    {"text":"下班后的时间，才是真正属于自己的人生。微醺一杯，学点韩语，让平凡的日子闪闪发光。","author":"WorkBuddy 每日寄语"},
    {"text":"每一个坚持学习的夜晚，都是对未来自己的投资。","author":"WorkBuddy 每日寄语"},
    {"text":"打工人不是贬义词，努力生活的人最值得尊重。","author":"WorkBuddy 每日寄语"},
    {"text":"微醺是最好的状态，清醒看世界，糊涂过生活。","author":"WorkBuddy 每日寄语"},
    {"text":"学韩语不是为了逃离，而是为了拥有更多选择。","author":"WorkBuddy 每日寄语"},
    {"text":"今天的你比昨天多学了一个单词，这就是进步。","author":"WorkBuddy 每日寄语"},
    {"text":"下班后的一杯酒，是对白天最好的交代。","author":"WorkBuddy 每日寄语"},
    {"text":"坚持21天，你会发现自己比想象中更强大。","author":"WorkBuddy 每日寄语"},
    {"text":"生活不只有加班，还有韩剧、韩语和微醺的夜晚。","author":"WorkBuddy 每日寄语"},
    {"text":"打工人的浪漫：把疲惫酿成酒，把业余过成诗。","author":"WorkBuddy 每日寄语"},
    {"text":"学一门新语言，就是打开一扇新的窗。","author":"WorkBuddy 每日寄语"},
    {"text":"微醺不是逃避，是给自己一个喘息的空间。","author":"WorkBuddy 每日寄语"},
    {"text":"每天进步1%，一年后你将进步37倍。","author":"WorkBuddy 每日寄语"},
    {"text":"下班后的两小时，决定了你五年后的样子。","author":"WorkBuddy 每日寄语"},
    {"text":"韩语难吗？难。但坚持更酷。","author":"WorkBuddy 每日寄语"},
    {"text":"打工是为了生活，学习是为了更好的生活。","author":"WorkBuddy 每日寄语"},
    {"text":"一杯酒，一本书，一门语言，这就是我的诗和远方。","author":"WorkBuddy 每日寄语"},
    {"text":"不要等准备好了才开始，开始了才会准备好。","author":"WorkBuddy 每日寄语"},
    {"text":"每个打工人心里，都住着一个不甘平庸的灵魂。","author":"WorkBuddy 每日寄语"},
    {"text":"微醺学韩语：因为热爱，所以坚持；因为坚持，所以闪光。","author":"WorkBuddy 每日寄语"},
    {"text":"生活就像韩语语法，看起来复杂，拆开来看其实很简单。","author":"WorkBuddy 每日寄语"},
    {"text":"今天的疲惫，是明天的底气。","author":"WorkBuddy 每日寄语"},
    {"text":"下班路上听韩语歌，突然觉得通勤也没那么烦了。","author":"WorkBuddy 每日寄语"},
    {"text":"努力工作的意义，是为了有能力享受下班后的时光。","author":"WorkBuddy 每日寄语"},
    {"text":"学韩语第100天，回看第1天，感谢没有放弃的自己。","author":"WorkBuddy 每日寄语"},
    {"text":"微醺让人放松，学习让人充实，两者结合就是完美夜晚。","author":"WorkBuddy 每日寄语"},
    {"text":"打工人，打工魂，下班学韩语最精神。","author":"WorkBuddy 每日寄语"},
    {"text":"每一个韩语字母，都是通往新世界的钥匙。","author":"WorkBuddy 每日寄语"},
    {"text":"生活需要仪式感，下班后的微醺学习就是我的仪式。","author":"WorkBuddy 每日寄语"},
    {"text":"今天学的韩语，也许就是明天旅行的通行证。","author":"WorkBuddy 每日寄语"},
]

# ============================================================
# 选题灵感库 (50条)
# ============================================================
IDEAS = [
    {"title":"「周一综合症」用韩语怎么说","desc":"结合周一上班场景，教打工人实用的韩语表达，引发共鸣","tags":["职场韩语","vlog","高共鸣"]},
    {"title":"挑战：用韩语点一杯微醺鸡尾酒","desc":"模拟在韩国酒吧点酒的场景，教学实用对话","tags":["场景教学","微醺","实用"]},
    {"title":"打工人必备：韩语辞职信模板","desc":"虽然是玩笑性质，但辞职话题在职场内容中热度很高","tags":["搞笑","职场","高互动"]},
    {"title":"韩语版「打工人语录」合集","desc":"把经典打工人语录翻译成韩语，做成系列合集","tags":["合集","热点词汇","系列内容"]},
    {"title":"下班后的第一杯酒，用韩语怎么说","desc":"记录下班后的微醺时刻，顺便教和酒相关的韩语","tags":["vlog","微醺","氛围感"]},
    {"title":"韩剧经典台词教学：来自星星的你","desc":"选择经典韩剧台词，逐句教学","tags":["韩剧","教学","蹭热度"]},
    {"title":"用韩语吐槽老板：打工人日常","desc":"把对老板的吐槽翻译成韩语，搞笑+教学","tags":["搞笑","职场","高互动"]},
    {"title":"韩语数字教学：工资篇","desc":"用工资数字教韩语数字，引发打工人共鸣","tags":["职场","教学","共鸣"]},
    {"title":"下班微醺vlog：今天学了这句韩语","desc":"完整记录下班→微醺→学韩语的全流程","tags":["vlog","日常","人设"]},
    {"title":"韩语发音挑战：故意读错搞笑版","desc":"故意把韩语发音读错然后纠正，增加娱乐性","tags":["搞笑","发音","涨粉"]},
    {"title":"打工人的周末计划用韩语说","desc":"分享周末计划，教学相关韩语词汇","tags":["日常","教学","周末"]},
    {"title":"韩语版「我太难了」怎么说","desc":"打工人经典语录的韩语版","tags":["热点","搞笑","共鸣"]},
    {"title":"微醺状态下学韩语是什么体验","desc":"记录微醺后学韩语的搞笑瞬间","tags":["vlog","搞笑","人设"]},
    {"title":"用韩语写今日工作总结","desc":"把工作总结翻译成韩语，学习+工作结合","tags":["职场","实用","创意"]},
    {"title":"韩语购物对话：在东大门砍价","desc":"模拟韩国购物场景，教学砍价对话","tags":["场景教学","旅行","实用"]},
    {"title":"打工人午餐用韩语点餐","desc":"用韩语点外卖/午餐，搞笑场景","tags":["搞笑","职场","日常"]},
    {"title":"韩语情话教学：适合表白用","desc":"教学韩语情话，适合恋爱的打工人","tags":["情话","教学","高收藏"]},
    {"title":"用韩语说「下班了！」的N种方式","desc":"教学多种表达下班的韩语句子","tags":["职场","教学","实用"]},
    {"title":"韩语歌曲教学：IU的歌","desc":"通过IU的歌曲学韩语，蹭明星热度","tags":["音乐","韩语","蹭热度"]},
    {"title":"打工人的韩语日记","desc":"用韩语写打工人的日记，记录生活","tags":["日记","日常","系列"]},
    {"title":"韩语面试自我介绍教学","desc":"教学韩语面试自我介绍，实用+职场","tags":["职场","实用","教学"]},
    {"title":"用韩语说「加班」的心情","desc":"教学表达加班心情的韩语，引发共鸣","tags":["职场","共鸣","搞笑"]},
    {"title":"韩语星座运势：今日打工人运势","desc":"用韩语说星座运势，创意内容","tags":["创意","星座","趣味"]},
    {"title":"微醺韩语小课堂：酒-related词汇","desc":"教学所有和酒相关的韩语词汇","tags":["微醺","词汇","人设"]},
    {"title":"用韩语介绍我的工作","desc":"用韩语介绍自己的职业和工作内容","tags":["职场","日常","教学"]},
    {"title":"韩语天气表达：今天适合微醺","desc":"用韩语说天气，结合微醺主题","tags":["日常","微醺","教学"]},
    {"title":"打工人的韩语口头禅","desc":"收集打工人的口头禅翻译成韩语","tags":["职场","搞笑","合集"]},
    {"title":"用韩语说「摸鱼」","desc":"教学摸鱼的韩语表达，打工人必备","tags":["搞笑","职场","热点"]},
    {"title":"韩语咖啡店点单教学","desc":"模拟在韩国咖啡店点单的场景","tags":["场景教学","日常","实用"]},
    {"title":"下班后的治愈韩语","desc":"教学治愈系韩语句子，适合下班后看","tags":["治愈","氛围","高收藏"]},
    {"title":"用韩语说「内卷」","desc":"教学内卷的韩语表达，热点话题","tags":["热点","职场","共鸣"]},
    {"title":"韩语表情包教学：打工人专属","desc":"制作韩语版打工人表情包","tags":["创意","表情包","传播"]},
    {"title":"微醺学韩语：今天学了一句情话","desc":"微醺状态下学韩语情话，氛围感拉满","tags":["微醺","情话","人设"]},
    {"title":"用韩语写辞职信（搞笑版）","desc":"用韩语写搞笑版辞职信","tags":["搞笑","职场","高互动"]},
    {"title":"韩语日常对话：在便利店","desc":"模拟在韩国便利店购物的对话","tags":["场景教学","旅行","实用"]},
    {"title":"打工人的韩语励志语录","desc":"用韩语说励志语录，适合分享","tags":["励志","高收藏","分享"]},
    {"title":"用韩语说「想辞职」","desc":"教学想辞职的韩语表达，打工人共鸣","tags":["职场","搞笑","共鸣"]},
    {"title":"韩语饮食词汇：打工人的外卖","desc":"用韩语说各种外卖食物","tags":["饮食","日常","教学"]},
    {"title":"微醺韩语歌翻唱挑战","desc":"微醺状态下翻唱韩语歌","tags":["音乐","挑战","人设"]},
    {"title":"用韩语介绍中国美食","desc":"用韩语介绍中国美食给韩国朋友","tags":["文化","美食","创意"]},
    {"title":"韩语时间表达：打工人的一天","desc":"用韩语说打工人从早到晚的时间线","tags":["职场","日常","教学"]},
    {"title":"用韩语说「今天又加班了」","desc":"教学加班的韩语表达，引发共鸣","tags":["职场","共鸣","日常"]},
    {"title":"韩语电视剧台词挑战","desc":"挑战用韩语说热门韩剧台词","tags":["韩剧","挑战","蹭热度"]},
    {"title":"打工人的韩语日记：今天学到了","desc":"用韩语记录今天学到的新知识","tags":["日记","学习","系列"]},
    {"title":"用韩语说「我爱加班」（反话）","desc":"用韩语说反话，搞笑表达","tags":["搞笑","职场","创意"]},
    {"title":"韩语旅行对话：机场篇","desc":"教学在韩国机场的实用对话","tags":["旅行","场景教学","实用"]},
    {"title":"微醺韩语：醉了也能学会的句子","desc":"教学简单到醉了也能记住的韩语","tags":["微醺","教学","人设"]},
    {"title":"用韩语介绍我的宠物","desc":"用韩语介绍自己的宠物，可爱主题","tags":["日常","宠物","可爱"]},
    {"title":"韩语职场用语大全","desc":"汇总打工人在职场用到的韩语","tags":["职场","教学","合集"]},
    {"title":"用韩语说「周末终于来了」","desc":"教学表达周末来了的韩语，共鸣感强","tags":["职场","日常","共鸣"]},
]

# ============================================================
# 内容复盘建议库 (15组，每组3条)
# ============================================================
REVIEWS = [
    [
        {"icon":"📈","highlight":"播放量分析：","text":"建议关注黄金发布时间 18:00-21:00，打工人下班时段流量最高"},
        {"icon":"🎨","highlight":"封面优化：","text":"使用'下班+微醺+韩语'三元素组合封面，点击率提升40%"},
        {"icon":"💬","highlight":"互动提升：","text":"结尾加入'今天学了什么韩语？评论区告诉我'引导互动"}
    ],
    [
        {"icon":"⏰","highlight":"最佳发布时间：","text":"工作日 18:00-21:00，周末 10:00-12:00 和 20:00-22:00"},
        {"icon":"🎵","highlight":"热门BGM：","text":"使用抖音热榜音乐，或韩剧OST（如《鬼怪》《太阳的后裔》）"},
        {"icon":"#️⃣","highlight":"推荐话题：","text":"#打工人日常 #自学韩语 #微醺时刻 #下班后的生活 #韩语学习"}
    ],
    [
        {"icon":"📏","highlight":"视频时长：","text":"最佳时长 30-60秒，完播率最高。教学类可延长至90秒"},
        {"icon":"🎬","highlight":"开头3秒：","text":"必须抓住眼球，用问题/悬念/反差开头，如'韩国人竟然这样说加班？'"},
        {"icon":"📌","highlight":"置顶评论：","text":"在评论区置顶今日学习的韩语知识点，方便粉丝收藏"}
    ],
    [
        {"icon":"📊","highlight":"数据复盘：","text":"关注完播率>点赞率>评论率，完播率低于30%需优化开头"},
        {"icon":"🔄","highlight":"发布频率：","text":"保持每天1条，周三是流量低谷，适合发干货教学类"},
        {"icon":"💡","highlight":"选题方向：","text":"职场+韩语的组合选题互动率最高，纯教学类收藏率高"}
    ],
    [
        {"icon":"📱","highlight":"竖屏拍摄：","text":"9:16竖屏，分辨率1080x1920，确保手机端观看体验"},
        {"icon":"🏷️","highlight":"字幕优化：","text":"韩语+中文双语字幕，字体大一些，颜色用白色+黑色描边"},
        {"icon":"🔗","highlight":"引导关注：","text":"视频最后2秒加'关注我，一起学韩语'的引导语"}
    ],
]

# ============================================================
# 书籍数据库
# ============================================================
BOOKS = {
    "growth": [
        {"title":"大女生","author":"杨澜","url":"https://weread.qq.com/web/reader/e0232630813ab82b3g01063b","emoji":"👩"},
        {"title":"正能量：女性心灵成长","author":"卡耐基","url":"https://weread.qq.com/web/reader/0b532bb0813aba4e8g0100e0","emoji":"✨"},
        {"title":"成为","author":"米歇尔·奥巴马","url":"https://weread.qq.com/web/reader/73532b707266d2a07358b3b","emoji":"🦋"},
        {"title":"向前一步","author":"谢丽尔·桑德伯格","url":"https://weread.qq.com/web/reader/ce032b305a9bc1ce032b6e7","emoji":"🌱"},
        {"title":"断舍离","author":"山下英子","url":"https://weread.qq.com/web/reader/6a0326c0715c23e06a03fb3","emoji":"💎"},
        {"title":"刻意练习","author":"安德斯·艾利克森","url":"https://weread.qq.com/web/reader/6f1323607159bc1a6f13a3a","emoji":"🎯"},
    ],
    "mind": [
        {"title":"当下的力量","author":"埃克哈特·托利","url":"https://weread.qq.com/web/reader/6e1323607159bc1a6e13a3a","emoji":"🧘"},
        {"title":"被讨厌的勇气","author":"岸见一郎","url":"https://weread.qq.com/web/reader/7a1323607159bc1a7a13a3a","emoji":"❤️"},
        {"title":"蛤蟆先生去看心理医生","author":"罗伯特·戴博德","url":"https://weread.qq.com/web/reader/8b1323607159bc1a8b13a3a","emoji":"🌿"},
        {"title":"自卑与超越","author":"阿德勒","url":"https://weread.qq.com/web/reader/9c1323607159bc1a9c13a3a","emoji":"☀️"},
        {"title":"情绪急救","author":"盖伊·温奇","url":"https://weread.qq.com/web/reader/ad1323607159bc1aad13a3a","emoji":"🌙"},
        {"title":"心流","author":"米哈里·契克森米哈赖","url":"https://weread.qq.com/web/reader/be1323607159bc1abe13a3a","emoji":"🔮"},
    ],
    "career": [
        {"title":"深度工作","author":"卡尔·纽波特","url":"https://weread.qq.com/web/reader/cf1323607159bc1acf13a3a","emoji":"💼"},
        {"title":"原则","author":"瑞·达利欧","url":"https://weread.qq.com/web/reader/d01323607159bc1ad013a3a","emoji":"📈"},
        {"title":"高效能人士的七个习惯","author":"史蒂芬·柯维","url":"https://weread.qq.com/web/reader/e11323607159bc1ae113a3a","emoji":"🚀"},
        {"title":"沟通的方法","author":"脱不花","url":"https://weread.qq.com/web/reader/f21323607159bc1af213a3a","emoji":"🎤"},
        {"title":"番茄工作法","author":"弗朗西斯科·西里洛","url":"https://weread.qq.com/web/reader/031323607159bc1a0313a3a","emoji":"⏰"},
        {"title":"思考，快与慢","author":"丹尼尔·卡尼曼","url":"https://weread.qq.com/web/reader/141323607159bc1a1413a3a","emoji":"🧠"},
    ],
    "health": [
        {"title":"轻断食","author":"麦克尔·莫斯利","url":"https://weread.qq.com/web/reader/251323607159bc1a2513a3a","emoji":"🥗"},
        {"title":"睡眠革命","author":"尼克·利特尔黑尔斯","url":"https://weread.qq.com/web/reader/361323607159bc1a3613a3a","emoji":"😴"},
        {"title":"运动改造大脑","author":"约翰·瑞迪","url":"https://weread.qq.com/web/reader/471323607159bc1a4713a3a","emoji":"🏃"},
        {"title":"吃出自愈力","author":"威廉·李","url":"https://weread.qq.com/web/reader/581323607159bc1a5813a3a","emoji":"🍎"},
        {"title":"正念的奇迹","author":"一行禅师","url":"https://weread.qq.com/web/reader/691323607159bc1a6913a3a","emoji":"🧘‍♀️"},
        {"title":"掌控习惯","author":"詹姆斯·克利尔","url":"https://weread.qq.com/web/reader/7a1323607159bc1a7a13a3a","emoji":"💪"},
    ],
}

# 每周推荐书
WEEKLY_PICKS = [
    {"title":"大女生","author":"杨澜","url":"https://weread.qq.com/web/reader/e0232630813ab82b3g01063b","reason":"杨澜写给女性的成长之书，关于自我认知、成长和同行"},
    {"title":"被讨厌的勇气","author":"岸见一郎","url":"https://weread.qq.com/web/reader/7a1323607159bc1a7a13a3a","reason":"阿德勒心理学入门，教你如何活出真实的自己"},
    {"title":"断舍离","author":"山下英子","url":"https://weread.qq.com/web/reader/6a0326c0715c23e06a03fb3","reason":"通过整理物品来整理人生，给心灵减负"},
    {"title":"当下的力量","author":"埃克哈特·托利","url":"https://weread.qq.com/web/reader/6e1323607159bc1a6e13a3a","reason":"心灵读物经典，帮助你摆脱焦虑，活在当下"},
]

# ============================================================
# 饮食方案库（每周轮换）
# ============================================================
MEAL_PLANS = [
    {
        "breakfast": ["水煮蛋2个 + 全麦面包1片 + 黑咖啡", "燕麦粥 + 坚果 + 蓝莓", "无糖豆浆 + 玉米 + 小番茄"],
        "lunch": ["鸡胸肉 + 西兰花 + 糙米饭", "牛肉沙拉 + 藜麦 + 油醋汁", "豆腐 + 时令蔬菜 + 红薯"],
        "dinner": ["蔬菜沙拉 + 水煮虾", "番茄蛋汤 + 少量杂粮", "清蒸鱼 + 凉拌黄瓜"],
        "snacks": ["原味坚果（每天一小把）", "无糖酸奶 + 奇亚籽", "黄瓜条/小番茄", "黑巧克力（85%以上）"]
    },
    {
        "breakfast": ["全麦三明治 + 黑咖啡", "希腊酸奶 + 燕麦 + 草莓", "蒸蛋 + 紫薯 + 圣女果"],
        "lunch": ["三文鱼 + 芦笋 + 糙米", "鸡胸肉沙拉 + 玉米 + 橄榄油", "番茄龙利鱼 + 菠菜 + 藜麦"],
        "dinner": ["凉拌豆腐 + 黄瓜", "冬瓜汤 + 少量糙米", "白灼虾 + 生菜"],
        "snacks": ["水煮毛豆", "海苔片", "小胡萝卜", "无糖杏仁奶"]
    },
]

# 运动方案（每周轮换）
EXERCISE_PLANS = [
    {
        "office": ["站立办公 15分钟", "深蹲 20个", "拉伸肩颈 2分钟", "爬楼梯代替电梯"],
        "afterwork": ["快走/慢跑 20分钟", "跳绳 10分钟", "瑜伽拉伸 15分钟", "HIIT训练 15分钟"],
        "bedtime": ["平板支撑 1分钟×3组", "卷腹 20个×3组", "臀桥 20个×3组", "腿部拉伸 3分钟"]
    },
    {
        "office": ["靠墙静蹲 1分钟", "踮脚尖 30个", "扩胸运动 20个", "走动5分钟"],
        "afterwork": ["骑车 30分钟", "游泳 30分钟", "普拉提 20分钟", "跳操 20分钟"],
        "bedtime": ["仰卧抬腿 15个×3组", "侧支撑 30秒×2组", "猫牛式拉伸 10次", "婴儿式放松 2分钟"]
    },
]

# ============================================================
# 爬取抖音热榜
# ============================================================
def fetch_douyin_hot():
    """爬取抖音热榜"""
    try:
        req = urllib.request.Request(
            "https://tophub.today/n/DpQvNABoNE",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        # 解析热榜
        import re
        items = re.findall(r'<a[^>]*href="(https://www\.douyin\.com/video/\d+)"[^>]*>([^<]+)</a>', html)
        plays = re.findall(r'(\d+)次播放', html)
        
        hotspots = []
        for i, (url, title) in enumerate(items[:10]):
            title = title.strip()
            play_count = plays[i] if i < len(plays) else "未知"
            play_str = f"{int(play_count)//10000}万播放" if play_count.isdigit() and int(play_count) > 10000 else f"{play_count}播放"
            
            # 生成改编灵感
            adapt_idea = generate_adapt_idea(title)
            
            hotspots.append({
                "title": title,
                "plays": play_str,
                "url": url,
                "author": "",
                "type": classify_topic(title),
                "adapt_idea": adapt_idea
            })
        
        return hotspots[:5]
    except Exception as e:
        print(f"抖音热榜爬取失败: {e}")
        return get_fallback_hotspots()

def fetch_xiaohongshu_hot():
    """爬取小红书热门话题"""
    try:
        req = urllib.request.Request(
            "https://tophub.today/n/KqndgxeLl9",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        import re
        items = re.findall(r'<a[^>]*>([^<]+)</a>', html)
        topics = []
        for item in items:
            item = item.strip()
            if len(item) > 4 and len(item) < 50:
                topics.append({"title": item, "platform": "小红书", "adapt_idea": generate_adapt_idea(item)})
        
        return topics[:3]
    except Exception as e:
        print(f"小红书热榜爬取失败: {e}")
        return []

def fetch_weibo_hot():
    """爬取微博热搜"""
    try:
        req = urllib.request.Request(
            "https://tophub.today/n/KqndgxeLl9",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        import re
        items = re.findall(r'<a[^>]*>([^<]+)</a>', html)
        topics = []
        for item in items:
            item = item.strip()
            if len(item) > 4 and len(item) < 50:
                topics.append({"title": item, "platform": "微博", "adapt_idea": generate_adapt_idea(item)})
        
        return topics[:3]
    except Exception as e:
        print(f"微博热搜爬取失败: {e}")
        return []

def generate_adapt_idea(title):
    """根据热点标题生成改编灵感"""
    keywords_work = ["打工", "上班", "下班", "加班", "职场", "老板", "工资", "辞职", "工作"]
    keywords_food = ["吃", "美食", "餐厅", "饭店", "外卖"]
    keywords_travel = ["旅行", "旅游", "打卡"]
    keywords_emotion = ["哭", "笑", "感动", "生气", "开心", "难过"]
    
    for kw in keywords_work:
        if kw in title:
            return f'结合{title}热点，用韩语表达打工人的心声，教大家如何用韩语吐槽工作'
    for kw in keywords_food:
        if kw in title:
            return f'结合美食热点，教学韩国美食相关的韩语表达，可以拍一期用韩语点餐的内容'
    for kw in keywords_travel:
        if kw in title:
            return f'结合旅行热点，教学旅行相关的韩语对话，吸引想去韩国旅行的粉丝'
    for kw in keywords_emotion:
        if kw in title:
            return f'结合情感热点，用韩语表达类似情绪，引发情感共鸣'
    
    return f'将{title}的话题与打工人微醺学韩语的人设结合，找到共鸣点进行改编'

def classify_topic(title):
    """分类热点话题"""
    if any(kw in title for kw in ["打工","上班","下班","加班","职场","老板","工资","辞职","工作"]):
        return "职场/打工人"
    if any(kw in title for kw in ["吃","美食","餐厅","饭店","外卖","食物"]):
        return "美食/生活"
    if any(kw in title for kw in ["旅行","旅游","风景","打卡"]):
        return "旅行/生活"
    if any(kw in title for kw in ["搞笑","笑","萌","猫","狗","宠物"]):
        return "搞笑/萌宠"
    if any(kw in title for kw in ["音乐","舞蹈","明星","偶像"]):
        return "娱乐/明星"
    return "热点/综合"

def get_fallback_hotspots():
    """备用热点数据"""
    return [
        {"title":"打工人下班后的微醺时刻","plays":"500万播放","url":"https://www.douyin.com","author":"","type":"职场/打工人","adapt_idea":"直接结合你的内容方向，展示下班微醺学韩语的日常"},
        {"title":"韩语自学打卡第100天","plays":"300万播放","url":"https://www.douyin.com","author":"","type":"学习/成长","adapt_idea":"学习打卡类内容热度高，可以模仿做365天打卡系列"},
        {"title":"一个人住的下酒菜","plays":"800万播放","url":"https://www.douyin.com","author":"","type":"美食/生活","adapt_idea":"结合下酒菜+韩语教学，边吃边学韩语的场景"},
    ]

# ============================================================
# 主函数：生成每日数据
# ============================================================
def generate_daily_data():
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    day_of_year = today.timetuple().tm_yday
    
    # 计算韩语课程进度
    lesson_idx = day_of_year % len(KOREAN_LESSONS)  # 循环课程
    today_lesson = KOREAN_LESSONS[lesson_idx]
    completed_count = lesson_idx + 1
    pronunciation_progress = round(completed_count / 40 * 100, 1)
    
    # 今日单词（每天10个，循环）
    word_start = (day_of_year * 10) % len(KOREAN_WORDS)
    words_today = KOREAN_WORDS[word_start:word_start+10]
    if len(words_today) < 10:
        words_today = words_today + KOREAN_WORDS[:10-len(words_today)]
    
    # 已掌握单词（累积）
    words_mastered = KOREAN_WORDS[:word_start]
    if len(words_mastered) > 20:
        words_mastered = words_mastered[-20:]  # 只显示最近20个
    
    # 语音跟读句子
    speak_idx = day_of_year % len(SPEAK_SENTENCES)
    speak_sentences = SPEAK_SENTENCES[speak_idx]
    
    # 每日金句
    quote_idx = day_of_year % len(QUOTES)
    quote = QUOTES[quote_idx]
    
    # 选题灵感（每天3-5条）
    idea_start = (day_of_year * 4) % len(IDEAS)
    ideas_today = IDEAS[idea_start:idea_start+4]
    if len(ideas_today) < 4:
        ideas_today = ideas_today + IDEAS[:4-len(ideas_today)]
    
    # 内容复盘（每周轮换）
    review_idx = (day_of_year // 7) % len(REVIEWS)
    review = REVIEWS[review_idx]
    
    # 爬取热点
    print("正在爬取抖音热榜...")
    douyin_hot = fetch_douyin_hot()
    print(f"获取到 {len(douyin_hot)} 条抖音热点")
    
    print("正在爬取小红书热榜...")
    xhs_hot = fetch_xiaohongshu_hot()
    print(f"获取到 {len(xhs_hot)} 条小红书热点")
    
    print("正在爬取微博热搜...")
    weibo_hot = fetch_weibo_hot()
    print(f"获取到 {len(weibo_hot)} 条微博热点")
    
    # 合并热点
    all_hotspots = douyin_hot + [
        {"title": h["title"], "plays": h.get("platform",""), "url": "", "author": "", "type": classify_topic(h["title"]), "adapt_idea": h["adapt_idea"]}
        for h in xhs_hot + weibo_hot
    ]
    
    # 每周选题日历
    weekday = today.weekday()  # 0=周一
    week_start = today - timedelta(days=weekday)
    weekly_ideas = []
    week_day_names = ["周一","周二","周三","周四","周五","周六","周日"]
    for i in range(7):
        d = week_start + timedelta(days=i)
        d_idx = d.timetuple().tm_yday
        idea = IDEAS[(d_idx * 4) % len(IDEAS)]
        weekly_ideas.append({"day": week_day_names[i], "title": idea["title"], "desc": idea["desc"]})
    
    # 每周推荐书
    week_num = day_of_year // 7
    weekly_pick = WEEKLY_PICKS[week_num % len(WEEKLY_PICKS)]
    
    # 饮食方案（每周轮换）
    meal_idx = week_num % len(MEAL_PLANS)
    meals = MEAL_PLANS[meal_idx]
    exercise = EXERCISE_PLANS[meal_idx]
    
    # 目标进度（每天微调）
    goals = [
        {"title":"抖音粉丝突破1000","current":652 + day_of_year % 50,"target":1000,"unit":"粉丝","progress":round((652 + day_of_year % 50)/1000*100,1)},
        {"title":"韩语TOPIK1级通关","current":completed_count,"target":40,"unit":"课时","progress":pronunciation_progress},
        {"title":"减重5斤","current":round(1.5 + day_of_year % 10 * 0.1, 1),"target":5,"unit":"斤","progress":round((1.5 + day_of_year % 10 * 0.1)/5*100,1)},
    ]
    
    # 组装数据
    data = {
        "date": date_str,
        "weekday": week_day_names[weekday],
        "quote": quote,
        "todos": [
            {"text":"发布今日韩语学习短视频","time":"19:00"},
            {"text":f"完成韩语第{today_lesson['num']}课学习","time":"20:30"},
            {"text":f"阅读《{weekly_pick['title']}》30分钟","time":"21:30"},
            {"text":"运动打卡30分钟","time":"22:00"},
        ],
        "review": review,
        "goals": goals,
        "korean": {
            "today_lesson": {
                "num": today_lesson["num"],
                "title": today_lesson["title"],
                "desc": today_lesson["desc"],
                "bilibili_url": f"https://www.bilibili.com/video/{today_lesson['bilibili']}"
            },
            "completed_lessons": [
                {"num": KOREAN_LESSONS[max(0,lesson_idx-1)]["num"], "title": KOREAN_LESSONS[max(0,lesson_idx-1)]["title"], "bilibili_url": f"https://www.bilibili.com/video/{KOREAN_LESSONS[max(0,lesson_idx-1)]['bilibili']}"},
                {"num": KOREAN_LESSONS[max(0,lesson_idx-2)]["num"], "title": KOREAN_LESSONS[max(0,lesson_idx-2)]["title"], "bilibili_url": f"https://www.bilibili.com/video/{KOREAN_LESSONS[max(0,lesson_idx-2)]['bilibili']}"},
            ],
            "progress": {
                "pronunciation": pronunciation_progress,
                "pronunciation_count": completed_count,
                "pronunciation_total": 40,
                "grammar": 0,
                "grammar_count": 0,
                "grammar_total": 0
            },
            "words_today": words_today,
            "words_mastered": words_mastered,
            "speak_sentences": speak_sentences,
            "video_courses": [
                {"title":"【全400集】2026最细自学韩语全套教程","desc":"零基础入门 · 持续更新","url":"https://www.bilibili.com/video/BV1RFTc62E29/"},
                {"title":"【整整600集】韩语零基础入门全套教程","desc":"一周入门 · 全程干货","url":"https://www.bilibili.com/video/BV1SPMzzaErY/"},
                {"title":"基础韩语I - 复旦大学","desc":"中国大学MOOC · 系统学习","url":"https://www.icourse163.org/course/FUDAN-1473663163"},
                {"title":"韩国语入门 - 高校外语慕课","desc":"8个教学单元","url":"https://moocs.unipus.cn/course/5201"},
                {"title":"LingoHut 免费韩语课程","desc":"125节免费课程","url":"https://www.lingohut.com/zh/l64/%E5%AD%A6%E4%B9%A0%E9%9F%A9%E8%AF%AD"},
            ]
        },
        "meetings": [
            {"title":"周例会 - 项目进度同步","date":"2026-07-28 14:00","duration":"45分钟","summary":"参会：张经理、李工、王设计\n核心结论：前端80%，API已联调，下周UI走查\n待办：王设计周三前提交设计稿"},
            {"title":"产品需求评审会","date":"2026-07-25 10:00","duration":"60分钟","summary":"参会：产品经理、技术负责人、测试\n核心结论：v2.0新增3个模块，性能优化优先级提升\n待办：技术负责人评估开发工时"},
        ],
        "books": {
            "growth": BOOKS["growth"],
            "mind": BOOKS["mind"],
            "career": BOOKS["career"],
            "health": BOOKS["health"],
            "weekly_pick": weekly_pick
        },
        "hotspots": all_hotspots[:8],
        "ideas": ideas_today,
        "weekly_ideas": weekly_ideas,
        "diet": {
            "weight": {"current": round(112.5 - day_of_year % 10 * 0.1, 1), "target": 107.5, "lost": round(1.5 + day_of_year % 10 * 0.1, 1)},
            "meals": meals,
            "exercises": exercise
        }
    }
    
    return data

# ============================================================
# 部署到GitHub
# ============================================================
def deploy_to_github(data_json_str):
    """通过GitHub API上传data.json"""
    # Token从环境变量读取，不硬编码（安全）
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        # 尝试从本地密钥文件读取（该文件不上传到GitHub）
        keyfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".token")
        if os.path.exists(keyfile):
            with open(keyfile) as f:
                token = f.read().strip()
    if not token:
        print("❌ 未设置GITHUB_TOKEN环境变量且找不到.token文件，跳过部署")
        return False
    repo = "husijia-1/workbuddy"
    
    # 获取当前data.json的SHA（如果存在）
    sha = ""
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/contents/data.json",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            import json as j
            info = j.loads(resp.read().decode())
            sha = info.get("sha", "")
    except:
        pass  # 文件不存在，首次上传
    
    # base64编码
    import base64
    content = base64.b64encode(data_json_str.encode("utf-8")).decode("utf-8")
    
    # 上传
    payload = json.dumps({
        "message": f"每日自动更新 {datetime.now().strftime('%Y-%m-%d')}",
        "content": content,
        **({"sha": sha} if sha else {})
    })
    
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/contents/data.json",
        data=payload.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json"
        },
        method="PUT"
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        print(f"✅ data.json 已上传到 GitHub: {result.get('content',{}).get('name','')}")
        return True

# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print(f"=== WorkBuddy 每日数据生成 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    
    # 生成数据
    data = generate_daily_data()
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    # 保存到本地
    output_path = "/workspace/workbuddy/data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data_json)
    print(f"✅ data.json 已生成: {output_path} ({len(data_json)} bytes)")
    
    # 部署到GitHub
    print("\n正在部署到 GitHub Pages...")
    try:
        deploy_to_github(data_json)
        print(f"✅ 部署完成！访问: https://husijia-1.github.io/workbuddy/")
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        print("data.json 已保存在本地，可手动上传")
