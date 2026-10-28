"""Builds public/episodes/ep02.json: one choreography, two languages."""
import json, pathlib

L = {
 'ar': dict(task='مهمة', you='أنت', result='النتيجة', search='بحث', read='قراءة', plan='الخطة', write='كتابة',
            review='مراجعة', publish='نشر', saved='محفوظ مرة', q='؟', what='ما الفرق؟',
            d_skill='تعليمات تحفظها مرة واحدة', d_agent='مساعد مستقل يعيد النتيجة', d_wf='خطة توزّع المهام بالترتيب', done='تم'),
 'en': dict(task='Task', you='You', result='Result', search='Research', read='Read', plan='Plan', write='Write',
            review='Review', publish='Publish', saved='saved once', q='?', what="What's the difference?",
            d_skill='Instructions saved once', d_agent='An independent helper', d_wf='A plan that orders the steps', done='done'),
}
TABS = ['SKILL', 'AGENT', 'WORKFLOW']

def hook(t):
    return dict(nodes=[
        dict(id='s', label='Skill', x=150, y=200, icon='doc', color=0),
        dict(id='a', label='Agent', x=430, y=200, icon='bot', color=1),
        dict(id='w', label='Workflow', x=710, y=200, icon='plan', color=2),
        dict(id='q', label='', x=430, y=580, icon='question', color='ink', w=210, h=170)],
      edges=[dict(id='sq', **{'from': 's', 'to': 'q'}, bend=-40), dict(id='aq', **{'from': 'a', 'to': 'q'}),
             dict(id='wq', **{'from': 'w', 'to': 'q'}, bend=40)],
      events=[dict(at=.04, do='show', node='s'), dict(at=.14, do='show', node='a'), dict(at=.24, do='show', node='w'),
              dict(at=.36, do='draw', edge='sq'), dict(at=.40, do='draw', edge='aq'), dict(at=.44, do='draw', edge='wq'),
              dict(at=.34, do='show', node='q'),
              dict(at=.52, do='packet', edge='sq', color=0, dur=.14), dict(at=.56, do='packet', edge='aq', color=1, dur=.14),
              dict(at=.60, do='packet', edge='wq', color=2, dur=.14), dict(at=.76, do='pulse', node='q'), dict(at=.86, do='pulse', node='q')],
      camera=[dict(at=0, zoom=1.08, x=0, y=40), dict(at=.5, zoom=1, x=0, y=0), dict(at=1, zoom=1.06, x=0, y=-30)])

def skill(t):
    ev = [dict(at=.03, do='show', node='f'), dict(at=.09, do='badge', node='f', text=t['saved']),
          dict(at=.13, do='show', node='c'), dict(at=.17, do='draw', edge='fc', dur=.06)]
    for i, (s0) in enumerate([.24, .48, .70]):
        n = f't{i+1}'
        ev += [dict(at=s0, do='show', node=n), dict(at=s0+.02, do='draw', edge=f'{n}c', dur=.05),
               dict(at=s0+.05, do='packet', edge=f'{n}c', dur=.07),
               dict(at=s0+.11, do='packet', edge='fc', color=0, dur=.07),
               dict(at=s0+.17, do='pulse', node='c'), dict(at=s0+.18, do='done', node=n),
               dict(at=s0+.18, do='badge', node='c', text=f'×{i+1}')]
    return dict(nodes=[
        dict(id='f', label='SKILL.md', x=170, y=190, icon='doc', color=0),
        dict(id='c', label='Claude', x=640, y=190, icon='spark', color='ink', w=210, h=170),
        dict(id='t1', label=f"{t['task']} 1", x=150, y=600, icon='pen', w=170, h=140),
        dict(id='t2', label=f"{t['task']} 2", x=430, y=620, icon='pen', w=170, h=140),
        dict(id='t3', label=f"{t['task']} 3", x=710, y=600, icon='pen', w=170, h=140)],
      edges=[dict(id='fc', **{'from': 'f', 'to': 'c'}, bend=-60),
             dict(id='t1c', **{'from': 't1', 'to': 'c'}, bend=40), dict(id='t2c', **{'from': 't2', 'to': 'c'}),
             dict(id='t3c', **{'from': 't3', 'to': 'c'}, bend=-30)],
      events=ev,
      camera=[dict(at=0, zoom=1.18, x=220, y=180), dict(at=.14, zoom=1.18, x=220, y=180), dict(at=.26, zoom=1, x=0, y=0),
              dict(at=1, zoom=1.04, x=0, y=0)])

def agent(t):
    return dict(nodes=[
        dict(id='u', label=t['you'], x=140, y=430, icon='user', color='ink', w=170, h=150),
        dict(id='g', label='Agent', x=620, y=430, icon='bot', color=1, w=220, h=180),
        dict(id='k1', label=t['search'], x=480, y=110, icon='search', color=1, w=160, h=130),
        dict(id='k2', label=t['read'], x=770, y=110, icon='eye', color=1, w=160, h=130),
        dict(id='k3', label='', x=620, y=690, icon='gear', color=1, w=130, h=110)],
      edges=[dict(id='ug', **{'from': 'u', 'to': 'g'}, bend=-90), dict(id='gu', **{'from': 'g', 'to': 'u'}, bend=-90),
             dict(id='g1', **{'from': 'g', 'to': 'k1'}), dict(id='g2', **{'from': 'g', 'to': 'k2'}),
             dict(id='g3', **{'from': 'g', 'to': 'k3'})],
      events=[dict(at=.03, do='show', node='u'), dict(at=.08, do='show', node='g'),
              dict(at=.13, do='draw', edge='ug', dur=.06), dict(at=.19, do='packet', edge='ug', label=t['task'], dur=.1),
              dict(at=.29, do='pulse', node='g'), dict(at=.30, do='spin', node='g', dur=.42),
              dict(at=.33, do='show', node='k1'), dict(at=.35, do='draw', edge='g1', dur=.04),
              dict(at=.38, do='packet', edge='g1', color=1, dur=.06), dict(at=.44, do='packet', edge='g1', color=1, dur=.06, reverse=True),
              dict(at=.47, do='show', node='k2'), dict(at=.49, do='draw', edge='g2', dur=.04),
              dict(at=.52, do='packet', edge='g2', color=1, dur=.06), dict(at=.58, do='packet', edge='g2', color=1, dur=.06, reverse=True),
              dict(at=.58, do='show', node='k3'), dict(at=.60, do='draw', edge='g3', dur=.04),
              dict(at=.63, do='packet', edge='g3', color=1, dur=.05), dict(at=.68, do='packet', edge='g3', color=1, dur=.05, reverse=True),
              dict(at=.73, do='done', node='g'), dict(at=.75, do='draw', edge='gu', dur=.06),
              dict(at=.80, do='packet', edge='gu', label=t['result'], color='good', dur=.1),
              dict(at=.90, do='pulse', node='u'), dict(at=.92, do='done', node='u')],
      camera=[dict(at=0, zoom=1, x=0, y=0), dict(at=.30, zoom=1.12, x=-90, y=60), dict(at=.70, zoom=1.12, x=-90, y=60),
              dict(at=.84, zoom=1, x=0, y=0)])

def workflow(t):
    steps = [('r', t['search'], 'search', 170, 380), ('w', t['write'], 'pen', 690, 380),
             ('v', t['review'], 'eye', 690, 660), ('p', t['publish'], 'send', 170, 660)]
    nodes = [dict(id='pl', label=t['plan'], x=430, y=100, icon='plan', color=2, w=200, h=140)]
    nodes += [dict(id=i, label=lb, x=x, y=y, icon=ic, color=2, w=180, h=140) for i, lb, ic, x, y in steps]
    edges = [dict(id=f'pl{i}', **{'from': 'pl', 'to': i}) for i, *_ in steps]
    chain = [('r', 'w'), ('w', 'v'), ('v', 'p')]
    edges += [dict(id=a+b, **{'from': a, 'to': b}) for a, b in chain]
    ev = [dict(at=.03, do='show', node='pl'), dict(at=.08, do='pulse', node='pl')]
    for k, (i, *_) in enumerate(steps):
        ev += [dict(at=.12+k*.05, do='show', node=i), dict(at=.13+k*.05, do='draw', edge=f'pl{i}', dur=.04)]
    for k, (a, b) in enumerate(chain):
        ev.append(dict(at=.36+k*.03, do='draw', edge=a+b, dur=.04))
    t0 = .45
    for k, (i, *_) in enumerate(steps):
        ev += [dict(at=t0, do='spin', node=i, dur=.07), dict(at=t0+.07, do='done', node=i)]
        if k < 3:
            a, b = chain[k]
            ev.append(dict(at=t0+.07, do='packet', edge=a+b, color=2, dur=.05))
        t0 += .12
    ev += [dict(at=.95, do='badge', node='pl', text='✓'), dict(at=.94, do='pulse', node='pl')]
    return dict(nodes=nodes, edges=edges, events=ev,
      camera=[dict(at=0, zoom=1.12, x=0, y=110), dict(at=.30, zoom=1, x=0, y=0), dict(at=.45, zoom=1.1, x=0, y=60),
              dict(at=.70, zoom=1.1, x=0, y=-80), dict(at=.92, zoom=1, x=0, y=0)])

p = pathlib.Path(__file__).resolve().parent.parent / 'public/episodes/ep02.json'
ep = json.loads(p.read_text())
for lang, t in L.items():
    sc = ep[lang]['scenes']
    keep = {s['type']: s for s in sc}
    # First run converts the static 'compare' scenes; later runs re-read the flow scenes (idempotent).
    old = [s for s in sc if s['type'] == 'compare'] or [s for s in sc if s['type'] == 'flow'][1:4]
    new = [dict(type='flow', term='Skill · Agent · Workflow', def_=t['what'], spec=hook(t), narration=sc[0]['narration'])]
    for i, (fn, d) in enumerate([(skill, t['d_skill']), (agent, t['d_agent']), (workflow, t['d_wf'])]):
        new.append(dict(type='flow', tabs=TABS, active=i, term=old[i]['term'], def_=d, spec=fn(t), narration=old[i]['narration']))
    new += [keep['trio'], keep['cta']]
    for s in new:
        if 'def_' in s: s['def'] = s.pop('def_')
    ep[lang]['scenes'] = new
p.write_text(json.dumps(ep, ensure_ascii=False, indent=1))
print('ok', [s['type'] for s in ep['ar']['scenes']])
