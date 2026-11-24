import sys,re,html
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
s=re.sub(r'(?is)<(script|style).*?</\1>','',s)
s=re.sub(r'(?i)</(p|div|tr|li|h\d)>','\n',s); s=re.sub(r'(?i)<br\s*/?>','\n',s); s=re.sub(r'(?i)</td>',' | ',s)
s=html.unescape(re.sub(r'<[^>]+>','',s)); s=re.sub(r'[ \t\xa0]+',' ',s); s=re.sub(r'\n\s*\n+','\n',s)
open(sys.argv[2],'w',encoding='utf-8').write(s)
