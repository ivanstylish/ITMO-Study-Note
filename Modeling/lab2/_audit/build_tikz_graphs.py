from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'TikZ'
OUT.mkdir(exist_ok=True)

def start():
    return [r'\begin{tikzpicture}[x=0.75pt,y=-0.75pt,>=latex]']

def node(k,x,y,r,font):
    return rf'\node[draw=black,circle,fill=white,line width=0.75pt,minimum size={r*1.5}pt,inner sep=0pt,font=\fontsize{{{font}}}{{{font+2}}}\selectfont] (S{k}) at ({x},{y}) {{S{k}}};'

def label(x,y,text,font=13.5,color='black'):
    return rf'\node[fill=white,inner sep=1.5pt,text={color},font=\fontsize{{{font}}}{{{font+2}}}\selectfont] at ({x},{y}) {{{text}}};'

def edge(a,b,color='black',width=.75):
    return rf'\draw[<->,draw={color},line width={width}pt] (S{a}) -- (S{b});'

# Positions and labels transcribed from the two supplied reference images.
p1={0:(46,228),1:(218,60),2:(218,228),3:(447,77),4:(218,397),5:(447,228),6:(447,379),7:(652,228),8:(793,228),9:(936,228),10:(1081,228)}
e1=[(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(4,5),(4,6),(3,7),(5,7),(6,7),(7,8),(8,9),(9,10)]
labels1=[(132,133,'0,05'),(132,215,'0,1'),(132,302,'0,35'),(333,58,'0,111111'),(282,100,'0,388889'),(397,120,'0,0625'),(280,273,'0,4375'),(397,265,'0,166667'),(333,376,'0,333333'),(550,142,'0,5'),(550,216,'0,5'),(550,292,'0,5'),(723,216,'0,5 / 0,3'),(865,216,'0,5 / 0,3'),(1009,216,'0,5 / 0,3')]
lines=start()+[node(k,*p,24,13.5) for k,p in p1.items()]+[edge(a,b) for a,b in e1]
lines += [label(x,y,t) for x,y,t in labels1]
lines += [label(570,446,'Вправо — указанная интенсивность; влево — 0,1 (до S7) или 0,3 (после S7).',11.25),r'\end{tikzpicture}']
(OUT/'system1.tikz').write_text('\n'.join(lines)+'\n',encoding='utf-8')

p2={}
for n1 in range(4):
    for n2 in range(3):
        for h,y in [(0,301),(1,60),(2,541)]:
            k=9*n1+3*n2+h
            p2[k]=(86+360.5*n1+103.5*n2,y+82*n2)
colors={'a':'{rgb,255:red,20;green,80;blue,136}','b':'{rgb,255:red,164;green,49;blue,26}','cA':'{rgb,255:red,41;green,111;blue,47}','cB':'{rgb,255:red,99;green,71;blue,145}'}
edges2=[]
for n1 in range(4):
    for n2 in range(3):
        for h in range(3):
            k=9*n1+3*n2+h
            if n1<3: edges2.append((k,k+9,'a'))
            if n2<2: edges2.append((k,k+3,'b'))
            if h==0:
                edges2.extend([(k,k+1,'cA'),(k,k+2,'cB')])
assert len(p1)==11 and len(e1)==15
assert len(p2)==36 and len(edges2)==75 and len(set((a,b) for a,b,_ in edges2))==75
lines=start()+[node(k,*p,20,12.75) for k,p in sorted(p2.items())]
lines += [edge(a,b,colors[c],1.0) for a,b,c in edges2]
for a,b,c in edges2:
    ax,ay=p2[a];bx,by=p2[b]
    x,y=(ax+bx)/2,(ay+by)/2
    if c=='a': y-=12
    elif c=='b': x+=13;y-=1
    else: x-=15
    lines.append(label(x,y,c,10.5,colors[c]))
lines += [label(1430,32,'h = A',15),label(1430,273,'h = 0',15),label(1430,513,'h = B',15)]
lines += [label(738,783,'a: n1 + 1 → 0,35;  n1 − 1 → 0,10.     b: n2 + 1 → 0,10;  n2 − 1 → 0,10.',14.25),label(738,812,'cA: 0 → A: 0,041549212;  A → 0: 0,166196846.',14.25),label(738,841,r'cB: 0 → B: 0,008450788;  B → 0: 0,033803154.     Все интенсивности в с⁻¹.',14.25),r'\end{tikzpicture}']
(OUT/'system2.tikz').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Created system1.tikz: 11 states / 30 directed arcs; system2.tikz: 36 states / 150 directed arcs')
