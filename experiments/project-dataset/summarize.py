
import json, glob, collections
total=0; classes=collections.Counter(); sw=0
for f in glob.glob("episodes/*.episodes.json"):
    eps=json.load(open(f)); total+=len(eps)
    if eps: sw+=1
    for e in eps: classes[e["class"]]+=1
print(f"Эпизодов: {total} в {sw} сессиях")
print(dict(classes))
