"""The 5 gap episodes (series "Claude from zero"), built from the verified fact sheets.

Every claim traces to an official help/privacy/research page (see SOURCES).
Rules baked in: Modern Standard Arabic, no company or government names (the
developer is "the company that makes Claude"), no hype, no "comment for the link".
`voice` = what the TTS reads (tashkeel, "كلود"); `narration` = what captions show.
Word anchors (`on`) make every motion land on the word that names it.

  python3 scripts/build-gap-episodes.py            # writes public/episodes/ep03..ep07.json
Existing audio/cues are preserved when the narration did not change.
"""
import json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
HANDLE = {'ar': '@اسم_القناة', 'en': '@your_channel'}
def B(ar, en): return {'__ar': ar, '__en': en}

def pick(v, lang):
    if isinstance(v, dict):
        if set(v) == {'__ar', '__en'}: return pick(v['__' + lang], lang)
        return {k: pick(x, lang) for k, x in v.items()}
    if isinstance(v, list): return [pick(x, lang) for x in v]
    return v

def node(id, label, x, y, icon=None, color=None, w=None, h=None):
    n = {'id': id, 'label': label, 'x': x, 'y': y}
    if icon: n['icon'] = icon
    if color is not None: n['color'] = color
    if w: n['w'] = w
    if h: n['h'] = h
    return n
def edge(id, a, b, bend=0): return {'id': id, 'from': a, 'to': b, **({'bend': bend} if bend else {})}
def ev(do, on=None, at=0.0, **k):
    e = {'at': at, 'do': do, **k}
    if on is not None: e['on'] = on
    return e

def mirror(spec):
    """English reads left→right: mirror the diagram (and edge bends) for the EN track."""
    s = json.loads(json.dumps(spec))
    for n in s['nodes']: n['x'] = 860 - n['x']
    for e in s['edges']:
        if 'bend' in e: e['bend'] = -e['bend']
    return s

# ---------------------------------------------------------------------------
EPISODES = {}

# ===== ep03 — Lesson 1: your first minute ==================================
EPISODES['ep03'] = dict(
    level='beginner', topic='أول دقيقة لك مع Claude',
    sources=[
        'https://support.claude.com/en/articles/8114491-getting-started-with-claude',
        'https://support.claude.com/en/articles/8325606-what-is-the-pro-plan',
        'https://support.claude.com/en/articles/8241126-upload-files-to-claude',
        'https://support.claude.com/en/articles/8664678',
        'https://claude.com/pricing',
        'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices',
    ],
    caption=B('الدرس 1 من سلسلة Claude من الصفر: من أين تبدأ، وأين تكتب وترفق ملفاتك، والعادة التي تغيّر جودة الردود.',
              'Lesson 1 of Claude from zero: where to start, where to type and attach, and the one habit that changes every answer.'),
    hashtags=B(['#Claude', '#ذكاء_اصطناعي', '#تعلم_الذكاء_الاصطناعي', '#مبتدئين'], ['#Claude', '#AI', '#LearnAI', '#Beginners']),
    scenes=[
        dict(type='hook', kicker=B('الدرس 1 · للمبتدئين', 'LESSON 1 · BEGINNER'),
             title=B('أول دقيقة لك\nمع *Claude*', 'Your first minute\nwith *Claude*'),
             body=B('أربع خطوات، وعادة واحدة تصنع الفرق.', 'Four steps, and one habit that changes everything.'),
             narration=B('أول دقيقة لك مع Claude: أربع خطوات بسيطة، وعادة واحدة تصنع الفرق كله.',
                         'Your first minute with Claude: four simple steps, and one habit that changes everything.'),
             voice=B('أوَّلُ دقيقةٍ لكَ مع كلود: أربعُ خطواتٍ بسيطة، وعادةٌ واحدةٌ تصنعُ الفرقَ كلَّه.', None)),
        dict(type='flow', def_=B('من أين تبدأ؟', 'Where do you start?'),
             narration=B('ابدأ من الموقع claude.ai، أو من تطبيق الحاسوب، أو تطبيق الهاتف. ثم أنشئ حسابًا مجانيًا ببريدك الإلكتروني، بشرط أن يكون عمرك 18 عامًا أو أكثر.',
                         'Start at claude.ai, or use the desktop app or the phone app. Then create a free account with your email. You need to be 18 or older.'),
             voice=B('ابدأْ من الموقع: كلود دوت إيه آي، أو من تطبيقِ الحاسوب، أو تطبيقِ الهاتف. ثم أنشِئْ حسابًا مجّانيًّا ببريدِك الإلكتروني، بشرطِ أن يكونَ عمرُك ثمانيةَ عشرَ عامًا أو أكثر.', None),
             spec=dict(
                 nodes=[node('u', B('أنت', 'You'), 430, 110, 'user', 'ink', 180, 140),
                        node('web', 'claude.ai', 150, 400, 'globe', 1),
                        node('desk', B('الحاسوب', 'Desktop'), 430, 400, 'laptop', 1),
                        node('mob', B('الهاتف', 'Phone'), 710, 400, 'phone', 1),
                        node('acc', B('حساب مجاني', 'Free account'), 430, 700, 'mail', 0, 260)],
                 edges=[edge('uw', 'u', 'web', 30), edge('ud', 'u', 'desk'), edge('um', 'u', 'mob', -30),
                        edge('wa', 'web', 'acc', -30), edge('da', 'desk', 'acc'), edge('ma', 'mob', 'acc', 30)],
                 events=[ev('show', None, 0.01, node='u'),
                         ev('draw', 'claude.ai', -0.04, edge='uw', dur=0.06), ev('show', 'claude.ai', 0, node='web'),
                         ev('draw', B('الحاسوب', 'desktop'), -0.04, edge='ud', dur=0.06), ev('show', B('الحاسوب', 'desktop'), 0, node='desk'),
                         ev('draw', B('الهاتف', 'phone'), -0.04, edge='um', dur=0.06), ev('show', B('الهاتف', 'phone'), 0, node='mob'),
                         ev('show', B('أنشئ', 'create'), 0, node='acc'),
                         ev('draw', B('أنشئ', 'create'), 0.01, edge='wa', dur=0.05), ev('draw', B('أنشئ', 'create'), 0.03, edge='da', dur=0.05),
                         ev('draw', B('أنشئ', 'create'), 0.05, edge='ma', dur=0.05),
                         ev('packet', B('ببريدك', 'email'), -0.02, edge='da', dur=0.1, label=B('بريدك الإلكتروني', 'your email'), color=0),
                         ev('badge', '18', 0, node='acc', text=B('+18', '18+')),
                         ev('done', B('أكثر', 'older'), 0, node='acc')])),
        dict(type='flow', def_=B('صندوق المحادثة', 'The chat box'),
             narration=B('هذا صندوق المحادثة: تكتب فيه طلبك ثم ترسله. وزر الإضافة يرفق ملفًا أو صورة. وبجانب زر الإرسال اسم النموذج، ومنه تختار. الحساب المجاني فيه Sonnet و Haiku.',
                         'This is the chat box: type your request, then send it. The plus button attaches a file or a photo. Next to the send button is the model name, tap it to choose. Free accounts get Sonnet and Haiku.'),
             voice=B('هذا صندوقُ المحادثة: تكتبُ فيه طلبَك ثم ترسلُه. وزرُّ الإضافةِ يُرفِقُ ملفًّا أو صورة. وبجانبِ زرِّ الإرسالِ اسمُ النموذج، ومنه تختار. الحسابُ المجّانيُّ فيه: سونِت، و هايكو.', None),
             spec=dict(
                 nodes=[node('box', B('اكتب طلبك هنا…', 'Type your request…'), 430, 170, 'chat', 'ink', 720, 140),
                        node('plus', B('ملف أو صورة', 'File or photo'), 140, 500, 'plus', 1, 220),
                        node('model', B('اختيار النموذج', 'Choose model'), 430, 560, 'gear', 2, 230),
                        node('send', B('إرسال', 'Send'), 720, 500, 'send', 0, 200)],
                 edges=[edge('bs', 'box', 'send', -20), edge('bp', 'box', 'plus', 20), edge('bm', 'box', 'model')],
                 events=[ev('show', None, 0.01, node='box'), ev('pulse', B('طلبك', 'request'), 0, node='box'),
                         ev('draw', B('ترسله', 'send'), -0.03, edge='bs', dur=0.05), ev('show', B('ترسله', 'send'), 0, node='send'),
                         ev('packet', B('ترسله', 'send'), 0.03, edge='bs', dur=0.08),
                         ev('draw', B('الإضافة', 'plus'), -0.03, edge='bp', dur=0.05), ev('show', B('الإضافة', 'plus'), 0, node='plus'),
                         ev('draw', B('النموذج', 'model'), -0.03, edge='bm', dur=0.05), ev('show', B('النموذج', 'model'), 0, node='model'),
                         ev('badge', 'Sonnet', 0, node='model', text='Sonnet · Haiku'), ev('pulse', 'Haiku', 0, node='model')])),
        dict(type='prompt', tone='bad', label=B('خطأ شائع: طلب بلا سياق', 'Common mistake: no context'),
             prompt=B('اكتب لي عن توفير الكهرباء', 'Write about saving electricity'),
             narration=B('الخطأ الأكثر شيوعًا في البداية: طلب عام بلا سياق. والنتيجة؟ رد عام مثله تمامًا.',
                         'The most common beginner mistake: a vague request with no context. The result? An answer just as vague.'),
             voice=B('الخطأُ الأكثرُ شيوعًا في البداية: طلبٌ عامٌّ بلا سياق. والنتيجة؟ ردٌّ عامٌّ مثلُه تمامًا.', None)),
        dict(type='chat', title=B('العادة الواحدة: *أعطه السياق*', 'The one habit: *give context*'),
             user=B('أنا مبتدئ، وأحضّر عرضًا مدته 5 دقائق لفريقي عن توفير الكهرباء في المكتب. أعطني 3 نقاط بسيطة، كل نقطة في جملة واحدة.',
                    "I'm a beginner preparing a 5-minute talk for my team about saving electricity at the office. Give me 3 simple points, one sentence each."),
             reply=B('1. أطفئ الشاشات والأجهزة عند مغادرة المكتب.\n2. استفد من ضوء النهار بدل الإضاءة الكاملة.\n3. اضبط التكييف على درجة معتدلة وثابتة.',
                     '1. Switch off screens and devices when you leave.\n2. Use daylight instead of full lighting.\n3. Keep the AC at a steady, moderate setting.'),
             replyTone='good',
             narration=B('العادة التي تغيّر كل شيء: أعطه السياق. من أنت، وماذا تريد، وبأي شكل. وهكذا يأتيك الرد على مقاسك.',
                         "The habit that changes everything: give it context. Who you are, what you need, and in what format. That's how the answer fits you."),
             voice=B('العادةُ التي تُغيِّرُ كلَّ شيء: أعطِه السياق. مَن أنت، وماذا تريد، وبأيِّ شكل. وهكذا يأتيكَ الردُّ على مقاسِك.', None)),
        dict(type='steps', title=B('الخلاصة', 'Recap'),
             items=B(['افتح claude.ai أو التطبيق', 'اكتب طلبك، وأرفق ملفك بزر +', 'قل من أنت، وماذا تريد، وبأي شكل'],
                     ['Open claude.ai or the app', 'Type your request, attach with +', 'Say who you are, what you need, what format']),
             itemsOn=B(['افتح', 'اكتب', 'عرّفه'], ['open', 'type', 'brief']),
             narration=B('الخلاصة: افتح Claude، واكتب طلبك وأرفق ما تحتاجه، ثم عرّفه بالمهمة كما تعرّف زميلًا جديدًا ذكيًا.',
                         "Recap: open Claude, type your request and attach what you need, then brief it the way you'd brief a smart new colleague."),
             voice=B('الخلاصة: افتحْ كلود، واكتبْ طلبَك وأرفِقْ ما تحتاجُه، ثم عرِّفْه بالمهمّةِ كما تُعرِّفُ زميلًا جديدًا ذكيًّا.', None)),
        dict(type='cta', title=B('احفظ الدرس', 'Save this lesson'),
             body=B('الدرس القادم: لماذا يوقفك Claude فجأة؟', 'Next: why Claude suddenly stops you'),
             narration=B('احفظ الدرس لترجع إليه. وفي الدرس القادم: لماذا يوقفك Claude فجأة في منتصف العمل؟',
                         'Save this lesson for later. Next time: why Claude suddenly stops you in the middle of your work.'),
             voice=B('احفظِ الدرسَ لترجعَ إليه. وفي الدرسِ القادم: لماذا يُوقِفُك كلود فجأةً في منتصفِ العمل؟', None)),
    ])

# ===== ep04 — Lesson 2: why Claude suddenly stops you ======================
EPISODES['ep04'] = dict(
    level='beginner', topic='لماذا يوقفك Claude فجأة؟ حدود الاستخدام',
    sources=[
        'https://support.claude.com/en/articles/11647753-understanding-usage-and-length-limits',
        'https://support.claude.com/en/articles/8114491-getting-started-with-claude',
        'https://support.claude.com/en/articles/8325606-what-is-the-pro-plan',
        'https://support.claude.com/en/articles/11049741-what-is-the-max-plan',
        'https://support.claude.com/en/articles/12466728-understanding-claude-error-messages',
        'https://support.claude.com/en/articles/9797557-usage-limit-best-practices',
    ],
    caption=B('الدرس 2: لماذا يتوقف Claude في منتصف العمل؟ كيف تعمل حدود الاستخدام، وما الذي يستهلكها، وثلاث نصائح رسمية.',
              'Lesson 2: why Claude stops mid-task. How usage limits work, what uses them up, and three official tips.'),
    hashtags=B(['#Claude', '#ذكاء_اصطناعي', '#نصائح', '#مبتدئين'], ['#Claude', '#AI', '#AITips', '#Beginners']),
    scenes=[
        dict(type='hook', kicker=B('الدرس 2 · للمبتدئين', 'LESSON 2 · BEGINNER'),
             title=B('توقف Claude فجأة؟\n*ليس عطلًا*', 'Claude stopped?\n*It is not broken*'),
             body=B('إنه حد الاستخدام، وهذه طريقة عمله.', "It's a usage limit. Here's how it works."),
             narration=B('توقف Claude فجأة في منتصف عملك؟ ليس عطلًا. إنه حد الاستخدام، وهذه طريقة عمله.',
                         "Claude stopped in the middle of your work? It's not broken. It's a usage limit, and here's how it works."),
             voice=B('توقَّفَ كلود فجأةً في منتصفِ عملِك؟ ليسَ عُطلًا. إنَّه حدُّ الاستخدام، وهذه طريقةُ عمَلِه.', None)),
        dict(type='flow', def_=B('نوعان من الحدود', 'Two kinds of limit'),
             narration=B('في الحساب المجاني حد للجلسة يتجدد كل خمس ساعات. والخطط المدفوعة لها حد أسبوعي أيضًا. وعندما تصل إلى الحد، تظهر رسالة فيها موعد التجديد.',
                         'On the free plan, a session limit resets every five hours. Paid plans also have a weekly limit. When you hit a limit, a message tells you when it resets.'),
             voice=B('في الحسابِ المجّاني حدٌّ للجلسةِ يتجدَّدُ كلَّ خمسِ ساعات. والخُطَطُ المدفوعةُ لها حدٌّ أسبوعيٌّ أيضًا. وعندما تصلُ إلى الحد، تظهرُ رسالةٌ فيها موعدُ التجديد.', None),
             spec=dict(
                 nodes=[node('s', B('حد الجلسة', 'Session limit'), 220, 200, 'clock', 0, 250, 160),
                        node('w', B('حد أسبوعي', 'Weekly limit'), 640, 200, 'clock', 2, 250, 160),
                        node('m', B('رسالة التجديد', 'Reset message'), 430, 620, 'warn', 1, 300, 160)],
                 edges=[edge('sm', 's', 'm', 30), edge('wm', 'w', 'm', -30)],
                 events=[ev('show', B('للجلسة', 'session'), -0.02, node='s'), ev('badge', B('خمس', 'five'), 0, node='s', text=B('كل 5 ساعات', 'every 5 h')),
                         ev('show', B('أسبوعي', 'weekly'), -0.02, node='w'), ev('badge', B('المدفوعة', 'Paid'), 0.02, node='w', text=B('للخطط المدفوعة', 'paid plans')),
                         ev('draw', B('وصلت', 'hit'), -0.03, edge='sm', dur=0.05), ev('draw', B('تصل', 'hit'), -0.01, edge='wm', dur=0.05),
                         ev('show', B('رسالة', 'message'), 0, node='m'),
                         ev('packet', B('رسالة', 'message'), 0.02, edge='sm', dur=0.08, color=0),
                         ev('badge', B('موعد', 'resets'), 0, node='m', text='5-hour limit reached'),
                         ev('pulse', B('التجديد', 'resets'), 0.02, node='m')])),
        dict(type='flow', def_=B('ما الذي يستهلك الرصيد أسرع؟', 'What uses it up faster?'),
             narration=B('ما الذي يستهلك الرصيد أسرع؟ المحادثات الطويلة، والملفات الكبيرة، والنماذج الأقوى، ومستوى الجهد الأعلى، وأدوات مثل البحث في الويب.',
                         'What uses it up faster? Long chats, big files, heavier models, higher effort, and tools like web search.'),
             voice=B('ما الذي يستهلكُ الرصيدَ أسرع؟ المحادثاتُ الطويلة، والملفّاتُ الكبيرة، والنماذجُ الأقوى، ومستوى الجُهدِ الأعلى، وأدواتٌ مثلُ البحثِ في الويب.', None),
             spec=dict(
                 nodes=[node('c', B('رصيد الاستخدام', 'Your usage'), 430, 420, 'clock', 'ink', 260, 170),
                        node('a', B('محادثة طويلة', 'Long chat'), 150, 120, 'chat', 0),
                        node('b', B('ملفات كبيرة', 'Big files'), 710, 120, 'folder', 0),
                        node('d', B('نموذج أقوى', 'Heavier model'), 110, 470, 'spark', 1),
                        node('e', B('جهد أعلى', 'Higher effort'), 750, 470, 'gear', 1),
                        node('f', B('البحث في الويب', 'Web search'), 430, 760, 'globe', 2, 240)],
                 edges=[edge('ac', 'a', 'c'), edge('bc', 'b', 'c'), edge('dc', 'd', 'c'), edge('ec', 'e', 'c'), edge('fc', 'f', 'c')],
                 events=[ev('show', None, 0.02, node='c'),
                         *[x for k, w in [('a', B('الطويلة', 'Long')), ('b', B('الكبيرة', 'big')), ('d', B('الأقوى', 'heavier')),
                                           ('e', B('الجهد', 'effort')), ('f', B('البحث', 'search'))]
                           for x in (ev('show', w, -0.02, node=k), ev('draw', w, 0, edge=k + 'c', dur=0.04),
                                     ev('packet', w, 0.04, edge=k + 'c', dur=0.07, color=1), ev('pulse', w, 0.1, node='c'))]])),
        dict(type='chat', title=B('النصيحة الأولى: *اجمع أسئلتك*', 'Tip 1: *batch your questions*'),
             attach=B('التقرير.pdf', 'report.pdf'),
             user=B('عندي 3 أسئلة عن التقرير نفسه. أجب عن كل سؤال في سطرين:\n1. ما أهم نتيجة؟\n2. ما أكبر خطر؟\n3. بماذا أبدأ؟',
                    'I have 3 questions about the same report. Answer each in 2 lines:\n1. What is the main finding?\n2. What is the biggest risk?\n3. What should I do first?'),
             reply=B('1. أهم نتيجة: نمو المبيعات في الربع الأخير.\n2. أكبر خطر: الاعتماد على عميل واحد.\n3. ابدأ بتنويع قاعدة العملاء.',
                     '1. Main finding: sales grew last quarter.\n2. Biggest risk: relying on one client.\n3. First step: widen your client base.'),
             replyTone='good',
             narration=B('النصيحة الأولى: اجمع الأسئلة المرتبطة في رسالة واحدة، بدل ثلاث رسائل منفصلة.',
                         'Tip one: put related questions in a single message, instead of three separate ones.'),
             voice=B('النصيحةُ الأولى: اجمعِ الأسئلةَ المرتبطةَ في رسالةٍ واحدة، بدلَ ثلاثِ رسائلَ منفصلة.', None)),
        dict(type='steps', title=B('ونصيحتان أخريان', 'Two more tips'),
             items=B(['محادثة طالت؟ ابدأ محادثة جديدة', 'ملفات تعود إليها؟ ضعها في Project'],
                     ['Long chat? Start a new one', 'Files you reuse? Put them in a Project']),
             itemsOn=B(['طالت', 'والملفات'], ['long', 'files']),
             narration=B('وإذا طالت المحادثة كثيرًا، فابدأ محادثة جديدة. والملفات التي تعود إليها دائمًا، ضعها في مشروع، لأن محتوى المشاريع يُحسب أقل عند إعادة استخدامه.',
                         'If a chat gets very long, start a new one. And files you keep coming back to belong in a Project, because project content counts less when it is reused.'),
             voice=B('وإذا طالتِ المحادثةُ كثيرًا، فابدأْ محادثةً جديدة. والملفّاتُ التي تعودُ إليها دائمًا، ضعْها في مشروع، لأنَّ محتوى المشاريعِ يُحسَبُ أقلَّ عند إعادةِ استخدامِه.', None)),
        dict(type='trio', title=B('ثلاث معلومات خاطئة', 'Three myths'),
             items=B([{'term': 'منتصف الليل', 'rule': 'الحد لا يتجدد عند منتصف الليل', 'icon': 'cross'},
                      {'term': 'التطبيق والموقع', 'rule': 'رصيد واحد مشترك، لا رصيدان', 'icon': 'cross'},
                      {'term': 'Max', 'rule': 'خطة أكبر، لكنها ليست بلا حدود', 'icon': 'cross'}],
                     [{'term': 'Midnight', 'rule': "Limits don't reset at midnight", 'icon': 'cross'},
                      {'term': 'App vs website', 'rule': 'One shared limit, not two', 'icon': 'cross'},
                      {'term': 'Max', 'rule': 'A bigger plan, but not unlimited', 'icon': 'cross'}]),
             itemsOn=B(['منتصف', 'التطبيق', 'Max'], ['midnight', 'app', 'Max']),
             narration=B('وثلاث معلومات خاطئة منتشرة: الحد لا يتجدد عند منتصف الليل. والتطبيق والموقع رصيد واحد. وحتى خطة Max لها حدود.',
                         "And three common myths: limits don't reset at midnight. The app and the website share one limit. And even the Max plan has limits."),
             voice=B('وثلاثُ معلوماتٍ خاطئةٍ منتشرة: الحدُّ لا يتجدَّدُ عند منتصفِ الليل. والتطبيقُ والموقعُ رصيدٌ واحد. وحتى خُطَّةُ ماكس لها حدود.', None)),
        dict(type='cta', title=B('احفظ الدرس', 'Save this lesson'),
             body=B('الدرس القادم: قبل أن تضغط «مشاركة»', 'Next: before you hit Share'),
             narration=B('احفظ الدرس. وفي الدرس القادم: ماذا يرى الآخرون فعلًا عندما تشارك محادثتك؟',
                         'Save this lesson. Next time: what other people actually see when you share a chat.'),
             voice=B('احفظِ الدرس. وفي الدرسِ القادم: ماذا يرى الآخرونَ فعلًا عندما تُشارِكُ محادثتَك؟', None)),
    ])

# ===== ep05 — Lesson 3: before you hit Share ===============================
path_spec = dict(
    nodes=[node('s', 'Settings', 710, 130, 'gear', 'ink', 220),
           node('p', 'Privacy', 430, 130, 'lock', 1, 220),
           node('c', 'Shared chats', 150, 130, 'link', 1, 230),
           node('m', 'Manage', 290, 520, 'plan', 2, 220),
           node('u', 'Unshare', 570, 520, 'cross', 0, 220)],
    edges=[edge('sp', 's', 'p'), edge('pc', 'p', 'c'), edge('cm', 'c', 'm', 30), edge('mu', 'm', 'u')],
    events=[ev('show', B('الإعدادات', 'Settings'), -0.01, node='s'),
            ev('draw', B('الخصوصية', 'Privacy'), -0.03, edge='sp', dur=0.04), ev('show', B('الخصوصية', 'Privacy'), 0, node='p'),
            ev('draw', B('المحادثات', 'Shared'), -0.03, edge='pc', dur=0.04), ev('show', B('المحادثات', 'Shared'), 0, node='c'),
            ev('draw', B('إدارة', 'Manage'), -0.03, edge='cm', dur=0.04), ev('show', B('إدارة', 'Manage'), 0, node='m'),
            ev('draw', B('إلغاء', 'Unshare'), -0.03, edge='mu', dur=0.04), ev('show', B('إلغاء', 'Unshare'), 0, node='u'),
            ev('packet', B('إلغاء', 'Unshare'), 0.02, edge='mu', dur=0.08, color='good'),
            ev('done', B('إلغاء', 'Unshare'), 0.12, node='u'),
            ev('badge', B('إلغاء', 'Unshare'), 0.12, node='u', text=B('إلغاء المشاركة', 'link off'))])
EPISODES['ep05'] = dict(
    level='beginner', topic='قبل أن تضغط مشاركة: خصوصيتك مع Claude',
    sources=[
        'https://privacy.claude.com/en/articles/10593882-share-and-unshare-chats',
        'https://support.claude.com/en/articles/16762437',
        'https://support.claude.com/en/articles/16762496-share-a-chat-with-specific-people',
        'https://privacy.claude.com/en/articles/12109829-how-do-i-change-my-model-improvement-privacy-setting',
        'https://support.claude.com/en/articles/12260368',
        'https://support.claude.com/en/articles/8325621-claude-data-privacy-faq',
    ],
    caption=B('الدرس 3: ماذا يرى الآخرون حين تشارك محادثة؟ وأين تلغي روابطك، ومتى تستخدم المحادثة الخفية، وما الذي لا تلصقه أبدًا.',
              'Lesson 3: what people see when you share a chat, where to switch links off, when to go incognito, and what never to paste.'),
    hashtags=B(['#Claude', '#خصوصية', '#ذكاء_اصطناعي', '#مبتدئين'], ['#Claude', '#Privacy', '#AI', '#Beginners']),
    scenes=[
        dict(type='hook', kicker=B('الدرس 3 · خصوصيتك', 'LESSON 3 · PRIVACY'),
             title=B('قبل أن تضغط\n*مشاركة*', 'Before you hit\n*Share*'),
             body=B('ماذا يرى الطرف الآخر فعلًا؟', 'What does the other person actually see?'),
             narration=B('قبل أن تضغط زر المشاركة، اعرف ماذا يرى الطرف الآخر فعلًا.',
                         'Before you hit Share, know what the other person actually sees.'),
             voice=B('قبلَ أن تضغطَ زرَّ المشاركة، اعرفْ ماذا يرى الطرفُ الآخرُ فعلًا.', None)),
        dict(type='flow', def_=B('ماذا يحدث عند المشاركة؟', 'What sharing does'),
             narration=B('المشاركة ترسل نسخة ثابتة من المحادثة لحظة مشاركتها. أما ملفاتك المرفقة فلا تُضمَّن. والرابط العام يفتحه أي شخص، حتى بدون حساب.',
                         'Sharing sends a fixed snapshot of the chat as it was at that moment. Your attached files are not included. And a public link opens for anyone, even without an account.'),
             voice=B('المشاركةُ تُرسِلُ نسخةً ثابتةً من المحادثةِ لحظةَ مشاركتِها. أمّا ملفّاتُك المرفقةُ فلا تُضمَّن. والرابطُ العامُّ يفتحُه أيُّ شخص، حتى بدونِ حساب.', None),
             spec=dict(
                 nodes=[node('chat', B('محادثتك', 'Your chat'), 710, 150, 'chat', 'ink', 230),
                        node('snap', B('نسخة ثابتة', 'Snapshot'), 430, 150, 'image', 0, 230),
                        node('file', B('ملفاتك', 'Your files'), 710, 520, 'folder', 'ink', 210),
                        node('link', B('رابط عام', 'Public link'), 150, 150, 'link', 2, 220),
                        node('who', B('أي شخص', 'Anyone'), 230, 560, 'users', 1, 230)],
                 edges=[edge('cs', 'chat', 'snap'), edge('sl', 'snap', 'link'), edge('lw', 'link', 'who', 20)],
                 events=[ev('show', None, 0.01, node='chat'),
                         ev('draw', B('نسخة', 'snapshot'), -0.03, edge='cs', dur=0.05), ev('show', B('نسخة', 'snapshot'), 0, node='snap'),
                         ev('packet', B('ثابتة', 'snapshot'), 0, edge='cs', dur=0.08, color=0),
                         ev('badge', B('لحظة', 'moment'), 0, node='snap', text=B('لحظة المشاركة', 'at that moment')),
                         ev('show', B('ملفاتك', 'files'), 0, node='file'), ev('badge', B('تُضمَّن', 'included'), 0, node='file', text=B('لا تُضمَّن', 'not included')),
                         ev('draw', B('الرابط', 'link'), -0.03, edge='sl', dur=0.05), ev('show', B('الرابط', 'link'), 0, node='link'),
                         ev('draw', B('شخص', 'anyone'), -0.03, edge='lw', dur=0.05), ev('show', B('شخص', 'anyone'), 0, node='who'),
                         ev('packet', B('شخص', 'anyone'), 0.02, edge='lw', dur=0.08, color=2),
                         ev('badge', B('حساب', 'account'), 0, node='who', text=B('بلا حساب', 'no account'))])),
        dict(type='steps', title=B('القاعدة البسيطة', 'The simple rule'),
             items=B(['الرابط العام = منشور عام', 'أي شخص يستطيع تصويره ونشره', 'إيقاف الرابط لا يحذف النسخ'],
                     ['A public link = a public post', 'Anyone can screenshot and repost it', "Turning it off doesn't delete copies"]),
             itemsOn=B(['منشور', 'تصويره', 'وإيقاف'], ['public', 'screenshot', 'off']),
             narration=B('والقاعدة البسيطة: تعامل مع الرابط العام كأنه منشور للعامة. فمن يفتحه يستطيع تصويره ونشره، وإيقاف الرابط لا يحذف النسخ التي انتشرت.',
                         "The simple rule: treat a public link like a public post. Anyone who opens it can screenshot and repost it, and turning the link off doesn't delete copies that spread."),
             voice=B('والقاعدةُ البسيطة: تعاملْ مع الرابطِ العامِّ كأنَّه منشورٌ للعامّة. فمَن يفتحُه يستطيعُ تصويرَه ونشرَه، وإيقافُ الرابطِ لا يحذفُ النُّسَخَ التي انتشرت.', None)),
        dict(type='flow', def_=B('أين ترى كل روابطك؟ (الواجهة بالإنجليزية)', 'Where to see every link you shared'),
             narration=B('لترى كل ما شاركته: الإعدادات، ثم الخصوصية، ثم المحادثات المشاركة، ثم إدارة، ثم إلغاء المشاركة.',
                         'To see everything you shared: Settings, then Privacy, then Shared chats, then Manage, then Unshare.'),
             voice=B('لترى كلَّ ما شاركتَه: الإعدادات، ثم الخصوصية، ثم المحادثاتُ المشارَكة، ثم إدارة، ثم إلغاءُ المشاركة.', None),
             spec=B(path_spec, mirror(path_spec))),
        dict(type='flow', def_=B('خياران يحميانك', 'Two settings that protect you'),
             narration=B('وفي الخصوصية خيار استخدام محادثاتك في تدريب النماذج، وأنت من يقرر تشغيله أو إيقافه. ولموضوع حساس، افتح محادثة خفية من أيقونة الشبح: لا تُحفظ في سجلك، ولا تُستخدم للتدريب، ويُحتفظ بها ثلاثين يومًا فقط.',
                         "Privacy also holds the setting for using your chats to train models, and you decide whether it's on or off. For something sensitive, open an incognito chat with the ghost icon: it isn't saved to your history, isn't used for training, and is kept for only thirty days."),
             voice=B('وفي الخصوصيةِ خيارُ استخدامِ محادثاتِك في تدريبِ النماذج، وأنتَ مَن يُقرِّرُ تشغيلَه أو إيقافَه. ولموضوعٍ حسّاس، افتحْ محادثةً خفيّةً من أيقونةِ الشبح: لا تُحفَظُ في سجلِّك، ولا تُستخدَمُ للتدريب، ويُحتفَظُ بها ثلاثينَ يومًا فقط.', None),
             spec=dict(
                 nodes=[node('t', 'Help Improve our AI models', 430, 140, 'gear', 2, 520, 140),
                        node('g', 'Incognito chat', 430, 520, 'ghost', 1, 300, 170)],
                 edges=[],
                 events=[ev('show', B('تدريب', 'train'), -0.03, node='t'), ev('badge', B('يقرر', 'decide'), 0, node='t', text=B('أنت تقرر', 'your choice')),
                         ev('pulse', B('إيقافه', 'off'), 0, node='t'),
                         ev('show', B('خفية', 'incognito'), -0.02, node='g'),
                         ev('badge', B('سجلك', 'history'), 0, node='g', text=B('لا يُحفظ في السجل', 'not in history')),
                         ev('badge', B('للتدريب#2', 'training'), 0, node='g', text=B('لا يُستخدم للتدريب', 'not for training')),
                         ev('badge', B('ثلاثين', 'thirty'), 0, node='g', text=B('30 يومًا فقط', '30 days only')),
                         ev('done', B('فقط', 'days'), 0.02, node='g')])),
        dict(type='trio', title=B('لا تلصق أبدًا', 'Never paste'),
             items=B([{'term': 'كلمات المرور', 'rule': 'ولا أي بيانات دخول', 'icon': 'lock'},
                      {'term': 'البطاقات والحسابات', 'rule': 'أرقام البطاقات والحسابات البنكية', 'icon': 'shield'},
                      {'term': 'السجلات الطبية', 'rule': 'والوثائق الشخصية السرية', 'icon': 'doc'}],
                     [{'term': 'Passwords', 'rule': 'or any login details', 'icon': 'lock'},
                      {'term': 'Cards & accounts', 'rule': 'card and bank account numbers', 'icon': 'shield'},
                      {'term': 'Medical records', 'rule': 'or confidential personal documents', 'icon': 'doc'}]),
             itemsOn=B(['المرور', 'البطاقات', 'السجلات'], ['passwords', 'card', 'medical']),
             narration=B('وقاعدة أخيرة: لا تلصق أبدًا كلمات المرور، ولا أرقام البطاقات والحسابات البنكية، ولا السجلات الطبية.',
                         'And one last rule: never paste passwords, card or bank account numbers, or medical records.'),
             voice=B('وقاعدةٌ أخيرة: لا تلصقْ أبدًا كلماتِ المرور، ولا أرقامَ البطاقاتِ والحساباتِ البنكيّة، ولا السجلّاتِ الطبيّة.', None)),
        dict(type='cta', title=B('احفظ الدرس', 'Save this lesson'),
             body=B('الدرس القادم: حوّل ملاحظاتك إلى اختبار', 'Next: turn your notes into a quiz'),
             narration=B('احفظ الدرس. وفي الدرس القادم: كيف تحوّل ملاحظاتك إلى اختبار يذاكر معك.',
                         'Save this lesson. Next time: how to turn your notes into a quiz that studies with you.'),
             voice=B('احفظِ الدرس. وفي الدرسِ القادم: كيفَ تُحوِّلُ ملاحظاتِك إلى اختبارٍ يُذاكِرُ معك.', None)),
    ])

# ===== ep06 — Lesson 4: notes → quiz =======================================
EPISODES['ep06'] = dict(
    level='beginner', topic='حوّل ملاحظاتك إلى اختبار مع Claude',
    sources=[
        'https://support.claude.com/en/articles/8241126-upload-files-to-claude',
        'https://support.claude.com/en/articles/9517075-what-are-projects',
        'https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects',
        'https://support.claude.com/en/articles/11139144-use-claude-for-education-at-your-university',
    ],
    caption=B('الدرس 4: ارفع صورة ملاحظاتك، واطلب اختبارًا سؤالًا بسؤال مع التصحيح والسبب، ولمادة كاملة استخدم Project.',
              'Lesson 4: upload a photo of your notes, ask for a one-question-at-a-time quiz with feedback, and use a Project for a whole course.'),
    hashtags=B(['#Claude', '#مذاكرة', '#طلاب', '#ذكاء_اصطناعي'], ['#Claude', '#StudyTips', '#Students', '#AI']),
    scenes=[
        dict(type='hook', kicker=B('الدرس 4 · للطلاب', 'LESSON 4 · STUDENTS'),
             title=B('حوّل ملاحظاتك\nإلى *اختبار*', 'Turn your notes\ninto a *quiz*'),
             body=B('بدل أن يعطيك الإجابات… يختبرك.', 'Instead of handing you answers, it tests you.'),
             narration=B('عندك امتحان؟ حوّل صورة ملاحظاتك إلى اختبار يذاكر معك، بدل أن يعطيك الإجابات جاهزة.',
                         'Exam coming up? Turn a photo of your notes into a quiz that studies with you, instead of handing you the answers.'),
             voice=B('عندَكَ امتحان؟ حوِّلْ صورةَ ملاحظاتِك إلى اختبارٍ يُذاكِرُ معك، بدلَ أن يُعطيَكَ الإجاباتِ جاهزة.', None)),
        dict(type='flow', def_=B('ارفع ملاحظاتك', 'Upload your notes'),
             narration=B('اضغط زر الإضافة، ثم Add files or photos، وارفع صورة واضحة لملاحظاتك أو ملف PDF. ويمكنك رفع حتى عشرين ملفًا في المحادثة الواحدة.',
                         'Tap the plus button, then Add files or photos, and upload a clear photo of your notes or a PDF. You can add up to twenty files in one chat.'),
             voice=B('اضغطْ زرَّ الإضافة، ثم Add files or photos، وارفعْ صورةً واضحةً لملاحظاتِك أو ملفَّ بي دي إف. ويمكنُك رفعُ حتى عشرينَ ملفًّا في المحادثةِ الواحدة.', None),
             spec=dict(
                 nodes=[node('plus', 'Add files or photos', 430, 120, 'plus', 0, 380, 140),
                        node('img', B('صورة واضحة', 'Clear photo'), 210, 470, 'image', 1, 240),
                        node('pdf', 'PDF', 650, 470, 'doc', 1, 220),
                        node('c', 'Claude', 430, 760, 'spark', 'ink', 220, 140)],
                 edges=[edge('pi', 'plus', 'img', 20), edge('pp', 'plus', 'pdf', -20), edge('ic', 'img', 'c', 20), edge('dc', 'pdf', 'c', -20)],
                 events=[ev('show', B('الإضافة', 'plus'), -0.02, node='plus'), ev('pulse', 'Add', 0, node='plus'),
                         ev('draw', B('صورة', 'photo'), -0.03, edge='pi', dur=0.05), ev('show', B('صورة', 'photo'), 0, node='img'),
                         ev('badge', B('واضحة', 'clear'), 0.02, node='img', text='1000×1000+'),
                         ev('draw', 'PDF', -0.03, edge='pp', dur=0.05), ev('show', 'PDF', 0, node='pdf'),
                         ev('show', B('عشرين', 'twenty'), -0.04, node='c'),
                         ev('draw', B('عشرين', 'twenty'), -0.03, edge='ic', dur=0.04), ev('draw', B('عشرين', 'twenty'), -0.01, edge='dc', dur=0.04),
                         ev('packet', B('عشرين', 'twenty'), 0.01, edge='ic', dur=0.08, color=1), ev('packet', B('عشرين', 'twenty'), 0.03, edge='dc', dur=0.08, color=1),
                         ev('badge', B('ملفًا', 'files'), 0, node='c', text=B('حتى 20 ملفًا', 'up to 20 files'))])),
        dict(type='chat', title=B('اطلب الاختبار *خطوة بخطوة*', 'Ask for the quiz *step by step*'),
             attach=B('ملاحظات.jpg', 'notes.jpg'),
             user=B('هذه ملاحظاتي في الأحياء. اختبرني بخمسة أسئلة اختيار من متعدد، سؤالًا واحدًا في كل مرة. انتظر إجابتي، وقل لي هل هي صحيحة ولماذا، ثم اسألني التالي. وفي النهاية اذكر المواضيع التي أخطأت فيها.',
                    "These are my biology notes. Quiz me with 5 multiple-choice questions, one at a time. Wait for my answer, tell me if I'm right and why, then ask the next one. At the end, list the topics I got wrong."),
             reply=B('السؤال 1 من 5:\nما العضية المسؤولة عن إنتاج الطاقة في الخلية؟\nأ. النواة\nب. الميتوكوندريا\nج. الريبوسوم',
                     'Question 1 of 5:\nWhich organelle produces energy for the cell?\nA. Nucleus\nB. Mitochondria\nC. Ribosome'),
             replyTone='tip',
             narration=B('ثم اطلب الاختبار بوضوح: سؤال واحد في كل مرة، وانتظر إجابتي، وصحّح لي مع السبب. هكذا يصبح مدرّسًا يسألك، لا ورقة إجابات.',
                         'Then ask for the quiz clearly: one question at a time, wait for my answer, correct me and say why. That turns it into a tutor that asks, not an answer sheet.'),
             voice=B('ثم اطلبِ الاختبارَ بوضوح: سؤالٌ واحدٌ في كلِّ مرّة، وانتظرْ إجابتي، وصحِّحْ لي مع السبب. هكذا يصبحُ مدرِّسًا يسألُك، لا ورقةَ إجابات.', None)),
        dict(type='flow', def_=B('حلقة المذاكرة', 'The study loop'),
             narration=B('سؤال، ثم إجابتك، ثم تصحيح مع السبب، وهكذا خمس مرات. وفي النهاية تعرف بالضبط ما الذي تحتاج إلى مراجعته.',
                         'A question, your answer, a correction with the reason, five times over. At the end you know exactly what to review.'),
             voice=B('سؤال، ثم إجابتُك، ثم تصحيحٌ مع السبب، وهكذا خمسَ مرّات. وفي النهايةِ تعرفُ بالضبطِ ما الذي تحتاجُ إلى مراجعتِه.', None),
             spec=dict(
                 nodes=[node('q', B('سؤال', 'Question'), 430, 110, 'question', 0, 210),
                        node('a', B('إجابتك', 'Your answer'), 150, 400, 'pen', 1, 210),
                        node('f', B('تصحيح + السبب', 'Feedback + why'), 710, 400, 'check', 'good', 240),
                        node('r', B('ما تراجعه', 'What to review'), 430, 720, 'bookmark', 2, 260)],
                 edges=[edge('qa', 'q', 'a', 30), edge('af', 'a', 'f', 60), edge('fq', 'f', 'q', 30), edge('fr', 'f', 'r', -20)],
                 events=[ev('show', B('سؤال', 'question'), -0.02, node='q'), ev('badge', B('سؤال', 'question'), 0, node='q', text='1/5'),
                         ev('draw', B('إجابتك', 'answer'), -0.03, edge='qa', dur=0.04), ev('show', B('إجابتك', 'answer'), 0, node='a'),
                         ev('draw', B('تصحيح', 'correction'), -0.03, edge='af', dur=0.04), ev('show', B('تصحيح', 'correction'), 0, node='f'),
                         ev('draw', B('وهكذا', 'five'), -0.04, edge='fq', dur=0.04),
                         *[x for k in range(4) for x in (
                             ev('packet', B('وهكذا', 'five'), 0.0 + k * 0.07, edge='qa', dur=0.025, color=0),
                             ev('packet', B('وهكذا', 'five'), 0.025 + k * 0.07, edge='af', dur=0.025, color=1),
                             ev('packet', B('وهكذا', 'five'), 0.05 + k * 0.07, edge='fq', dur=0.02, color='good'),
                             ev('badge', B('وهكذا', 'five'), 0.07 + k * 0.07, node='q', text=f'{k + 2}/5'))],
                         ev('show', B('النهاية', 'end'), 0, node='r'), ev('draw', B('النهاية', 'end'), 0, edge='fr', dur=0.05),
                         ev('done', B('مراجعته', 'review'), 0, node='r')])),
        dict(type='steps', title=B('لمادة كاملة: Project', 'For a whole course: a Project'),
             items=B(['Projects ثم + New Project', 'ارفع ملفات المادة مرة واحدة', 'الحساب المجاني: حتى 5 مشاريع'],
                     ['Projects, then + New Project', 'Upload the course files once', 'Free accounts: up to 5 Projects']),
             itemsOn=B(['أنشئ', 'وارفع', 'خمسة'], ['create', 'upload', 'five']),
             narration=B('ولمادة كاملة، أنشئ مشروعًا وارفع ملفات المادة مرة واحدة، فترجع إليها في كل محادثة داخله. والحساب المجاني يتيح حتى خمسة مشاريع.',
                         'For a whole course, create a Project and upload the course files once, so every chat inside it can use them. Free accounts get up to five Projects.'),
             voice=B('ولمادّةٍ كاملة، أنشِئْ مشروعًا وارفعْ ملفّاتِ المادّةِ مرّةً واحدة، فترجعُ إليها في كلِّ محادثةٍ داخلَه. والحسابُ المجّانيُّ يُتيحُ حتى خمسةِ مشاريع.', None)),
        dict(type='cta', title=B('احفظ الدرس', 'Save this lesson'),
             body=B('استخدمه ليختبرك، لا ليحل واجباتك.', 'Use it to test you, not to do your homework.'),
             narration=B('تذكّر: استخدمه ليختبرك، لا ليحل الواجبات المطلوبة منك. وفي الدرس القادم: هل Claude ألطف معك بالعربية؟',
                         'Remember: use it to test you, not to do the work you are meant to do yourself. Next time: is Claude gentler with you in Arabic?'),
             voice=B('تذكَّرْ: استخدمْه ليختبرَك، لا ليَحُلَّ الواجباتِ المطلوبةَ منك. وفي الدرسِ القادم: هل كلود ألطفُ معك بالعربية؟', None)),
    ])

# ===== ep07 — Lesson 5: gentler in Arabic? ask for critique =================
EPISODES['ep07'] = dict(
    level='beginner', topic='هل Claude ألطف بالعربية؟ وكيف تطلب نقدًا صريحًا',
    sources=[
        'https://www.anthropic.com/research/claude-values-models-languages',
        'https://www-cdn.anthropic.com/files/4zrzovbb/website/02da7f28f74daa1be526d3ded451a4efc86bccdc.pdf',
        'https://www.anthropic.com/constitution',
        'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices',
        'https://support.claude.com/en/articles/10185728',
    ],
    caption=B('الدرس 5: دراسة نشرتها الجهة المطوّرة لـ Claude في يوليو 2026 وجدت ميلًا أكبر إلى المسايرة والدفء في الردود العربية. هذه حدود الدراسة، وطريقة الحصول على نقد صريح.',
              "Lesson 5: a July 2026 study by Claude's own developer found Arabic replies lean more toward deference and warmth. Here are its limits, and how to get honest critique."),
    hashtags=B(['#Claude', '#ذكاء_اصطناعي', '#اللغة_العربية', '#نصائح'], ['#Claude', '#AI', '#Arabic', '#AITips']),
    scenes=[
        dict(type='hook', kicker=B('الدرس 5 · بالعربية', 'LESSON 5 · ARABIC'),
             title=B('هل Claude *ألطف*\nبالعربية؟', 'Is Claude *gentler*\nin Arabic?'),
             body=B('دراسة من الجهة التي طوّرته.', 'A study by the team that built it.'),
             narration=B('هل Claude ألطف معك بالعربية منه بالإنجليزية؟ دراسة نشرتها الجهة التي طوّرته تقول: يميل إلى ذلك.',
                         'Is Claude gentler with you in Arabic than in English? A study published by the team that built it says it leans that way.'),
             voice=B('هل كلود ألطفُ معكَ بالعربيةِ منه بالإنجليزية؟ دراسةٌ نشرَتْها الجهةُ التي طوَّرَتْه تقول: يميلُ إلى ذلك.', None)),
        dict(type='flow', def_=B('الدراسة', 'The study'),
             narration=B('حللت الدراسة أكثر من ثلاثمئة ألف محادثة بعشرين لغة، ونُشرت في يوليو 2026.',
                         'It analysed more than three hundred thousand conversations in twenty languages, and was published in July 2026.'),
             voice=B('حلَّلَتِ الدراسةُ أكثرَ من ثلاثِمئةِ ألفِ محادثة بعشرينَ لغة، ونُشِرَتْ في يوليو ألفين وستةٍ وعشرين.', None),
             spec=dict(
                 nodes=[node('n', B('+300 ألف محادثة', '300k+ chats'), 220, 160, 'chat', 0, 290),
                        node('l', B('20 لغة', '20 languages'), 640, 160, 'globe', 1, 250),
                        node('r', B('النتائج', 'Findings'), 430, 560, 'scale', 2, 260, 160)],
                 edges=[edge('nr', 'n', 'r', 20), edge('lr', 'l', 'r', -20)],
                 events=[ev('show', B('ثلاثمئة', 'three'), -0.02, node='n'), ev('show', B('بعشرين', 'twenty'), -0.02, node='l'),
                         ev('draw', B('ونُشرت', 'published'), -0.06, edge='nr', dur=0.05), ev('draw', B('ونُشرت', 'published'), -0.04, edge='lr', dur=0.05),
                         ev('show', B('ونُشرت', 'published'), -0.01, node='r'),
                         ev('packet', B('ونُشرت', 'published'), 0, edge='nr', dur=0.08, color=0), ev('packet', B('ونُشرت', 'published'), 0.02, edge='lr', dur=0.08, color=1),
                         ev('badge', '2026', 0, node='r', text=B('يوليو 2026', 'July 2026'))])),
        dict(type='flow', def_=B('ماذا وجدت؟ (متوسطات)', 'What it found (averages)'),
             narration=B('بالإنجليزية يميل أكثر إلى التدقيق والحذر والتعمق. وبالعربية يميل أكثر إلى المسايرة والدفء والإيجاز.',
                         'In English it leans more toward rigor, caution and depth. In Arabic it leans more toward deference, warmth and brevity.'),
             voice=B('بالإنجليزيةِ يميلُ أكثرَ إلى التدقيقِ والحذرِ والتعمُّق. وبالعربيةِ يميلُ أكثرَ إلى المسايرةِ والدفءِ والإيجاز.', None),
             spec=dict(
                 nodes=[node('en', 'English', 210, 120, 'globe', 1, 250, 140),
                        node('ar', B('العربية', 'Arabic'), 650, 120, 'globe', 0, 250, 140),
                        node('e1', B('تدقيق', 'Rigor'), 210, 330, None, 1, 220, 100),
                        node('e2', B('حذر', 'Caution'), 210, 470, None, 1, 220, 100),
                        node('e3', B('تعمّق', 'Depth'), 210, 610, None, 1, 220, 100),
                        node('a1', B('مسايرة', 'Deference'), 650, 330, None, 0, 220, 100),
                        node('a2', B('دفء', 'Warmth'), 650, 470, None, 0, 220, 100),
                        node('a3', B('إيجاز', 'Brevity'), 650, 610, None, 0, 220, 100)],
                 edges=[],
                 events=[ev('show', B('بالإنجليزية', 'English'), -0.02, node='en'),
                         ev('show', B('التدقيق', 'rigor'), 0, node='e1'), ev('show', B('والحذر', 'caution'), 0, node='e2'), ev('show', B('والتعمق', 'depth'), 0, node='e3'),
                         ev('show', B('وبالعربية', 'Arabic'), -0.02, node='ar'),
                         ev('show', B('المسايرة', 'deference'), 0, node='a1'), ev('show', B('والدفء', 'warmth'), 0, node='a2'), ev('show', B('والإيجاز', 'brevity'), 0, node='a3'),
                         ev('pulse', B('المسايرة', 'deference'), 0.02, node='ar')])),
        dict(type='steps', title=B('لكن انتبه', 'But note'),
             items=B(['متوسطات، لا حكم على كل محادثة', 'على نماذج أقدم من الحالية', 'السبب غير معروف بعد'],
                     ['Averages, not every chat', 'Measured on older models', 'The cause is not yet known']),
             itemsOn=B(['متوسطات', 'أقدم', 'السبب'], ['averages', 'older', 'why']),
             narration=B('لكن انتبه: هذه متوسطات وليست حكمًا على كل محادثة، وقيست على نماذج أقدم من الحالية، والجهة نفسها تقول إنها لا تعرف السبب بعد.',
                         "But note: these are averages, not a verdict on every chat, they were measured on older models, and the team itself says it doesn't yet know why."),
             voice=B('لكنِ انتبِهْ: هذه متوسِّطاتٌ وليستْ حُكمًا على كلِّ محادثة، وقِيسَتْ على نماذجَ أقدمَ من الحالية، والجهةُ نفسُها تقولُ إنَّها لا تعرفُ السببَ بعد.', None)),
        dict(type='chat', title=B('الحل: *اطلب النقد صراحة*', 'The fix: *ask for critique*'),
             attach=B('خطة المشروع.pdf', 'project-plan.pdf'),
             user=B('راجع خطة مشروعي المرفقة بصراحة تامة. أريد نقدًا لا مجاملة: اذكر أهم 3 نقاط ضعف، وأكبر خطر، وما الذي قد يجعلها تفشل. لا تبدأ بالمديح.',
                    "Review my attached project plan with complete honesty. I want critique, not compliments: list the 3 biggest weaknesses, the biggest risk, and what could make it fail. Don't start with praise."),
             reply=B('أهم 3 نقاط ضعف:\n1. التكلفة أعلى من الإيراد المتوقع في السنة الأولى.\n2. لا توجد خطة تسويق واضحة.\n3. الاعتماد على مورد واحد.\nأكبر خطر: نفاد السيولة قبل الشهر السادس.',
                     'The 3 biggest weaknesses:\n1. Costs exceed expected revenue in year one.\n2. There is no clear marketing plan.\n3. You rely on a single supplier.\nBiggest risk: running out of cash before month six.'),
             replyTone='tip',
             narration=B('والحل: اطلب النقد صراحة، وقل لماذا تحتاجه. ولا تكتفِ بسؤال: ما رأيك؟',
                         "The fix: ask for critique explicitly, and say why you need it. Don't settle for: what do you think?"),
             voice=B('والحلّ: اطلبِ النقدَ صراحةً، وقلْ لماذا تحتاجُه. ولا تكتفِ بسؤال: ما رأيُك؟', None)),
        dict(type='steps', title=B('اجعلها دائمة', 'Make it permanent'),
             items=B(['افتح Settings', 'ثم Your Claude', 'ثم Instructions: أريد نقدًا صريحًا'],
                     ['Open Settings', 'Then Your Claude', 'Then Instructions: I want honest critique']),
             itemsOn=B(['الإعدادات', 'Your', 'التعليمات'], ['Settings', 'Your', 'Instructions']),
             narration=B('ولتجعلها دائمة: من الإعدادات، ثم Your Claude، ثم التعليمات، اكتب أنك تريد نقدًا صريحًا في كل محادثة.',
                         'To make it permanent: go to Settings, then Your Claude, then Instructions, and write that you want honest critique in every chat.'),
             voice=B('ولتجعلَها دائمة: من الإعدادات، ثم Your Claude، ثم التعليمات، اكتبْ أنَّك تريدُ نقدًا صريحًا في كلِّ محادثة.', None)),
        dict(type='cta', title=B('احفظ الدرس', 'Save this lesson'),
             body=B('إذا أردت النقد، فاطلب النقد.', 'If you want critique, ask for critique.'),
             narration=B('القاعدة: إذا أردت النقد، فاطلب النقد، بأي لغة. احفظ الدرس.',
                         'The rule: if you want critique, ask for critique, in any language. Save this lesson.'),
             voice=B('القاعدة: إذا أردتَ النقد، فاطلبِ النقد، بأيِّ لغة. احفظِ الدرس.', None)),
    ])

# ---------------------------------------------------------------------------
def build(ep_id, e):
    path = root / 'public/episodes' / f'{ep_id}.json'
    old = json.loads(path.read_text()) if path.exists() else None
    out = {'id': ep_id, 'level': e['level'], 'topic': e['topic'], 'channel': HANDLE, 'sources': e['sources']}
    for lang in ('ar', 'en'):
        scenes = []
        for i, sc in enumerate(e['scenes']):
            s = pick(sc, lang)
            if 'def_' in s: s['def'] = s.pop('def_')
            if not s.get('voice'): s.pop('voice', None)
            if old:  # keep synced audio when the words did not change
                o = old[lang]['scenes'][i] if i < len(old[lang]['scenes']) else {}
                if o.get('narration') == s['narration'] and o.get('voice') == s.get('voice'):
                    for k in ('audio', 'cues', '_heard'):
                        if k in o: s[k] = o[k]
            scenes.append(s)
        out[lang] = {'dir': 'rtl' if lang == 'ar' else 'ltr', 'caption': pick(e['caption'], lang),
                     'hashtags': pick(e['hashtags'], lang), 'scenes': scenes}
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print('wrote', path.name, len(out['ar']['scenes']), 'scenes')

for k, v in EPISODES.items(): build(k, v)
