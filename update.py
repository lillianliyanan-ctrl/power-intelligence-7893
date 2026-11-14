"""Fetch RSS feeds and optionally summarize with OpenAI. Standard library only."""
import os, json, re, hashlib, datetime, urllib.request, urllib.parse, xml.etree.ElementTree as ET, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data/articles.json'
FEEDS=[('Data Center Dynamics','https://www.datacenterdynamics.com/en/rss/','Market & Customers'),('The Register - Data Centre','https://www.theregister.com/data_centre/headlines.atom','Technology'),('Google News - UPS power','https://news.google.com/rss/search?q='+urllib.parse.quote('data center UPS power Vertiv Eaton Schneider Electric when:7d')+'&hl=en-US&gl=US&ceid=US:en','Competitors'),('Google News - Power infrastructure','https://news.google.com/rss/search?q='+urllib.parse.quote('data center power infrastructure grid liquid cooling 800V DC when:7d')+'&hl=en-US&gl=US&ceid=US:en','Technology')]
KEYWORDS=['data center','datacenter','ups','uninterruptible','vertiv','eaton','schneider','abb','power','grid','cooling','800v','prefab','electrical','energy']
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()[:1600]
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'PowerIntelligence/1.0 (+personal RSS reader)'})
 with urllib.request.urlopen(req,timeout=18) as resp:return resp.read()
def parse(xml,source,topic):
 root=ET.fromstring(xml);items=[]
 for item in root.findall('.//item')[:25]:
  title=clean(item.findtext('title'));link=(item.findtext('link') or '').strip();description=clean(item.findtext('description'));date=item.findtext('pubDate') or ''
  items.append((title,link,description,date))
 ns={'a':'http://www.w3.org/2005/Atom'}
 for item in root.findall('.//a:entry',ns)[:25]:
  title=clean(item.findtext('a:title',default='',namespaces=ns));ln=item.find('a:link',ns);link=ln.get('href','') if ln is not None else '';description=clean(item.findtext('a:summary',default='',namespaces=ns));date=item.findtext('a:updated',default='',namespaces=ns);items.append((title,link,description,date))
 for title,link,description,date in items:
  if not title or not link or not any(k in (title+' '+description).lower() for k in KEYWORDS):continue
  try:
   from email.utils import parsedate_to_datetime
   day=parsedate_to_datetime(date).date().isoformat()
  except Exception:day=date[:10] if re.match(r'\d{4}-\d\d-\d\d',date) else ''
  ident=hashlib.sha256((title.lower().strip()).encode()).hexdigest()[:20]
  yield {'id':ident,'title':title,'title_zh':title,'summary_zh':description[:350] or '点击原文阅读详情。','source':source,'published':day,'topic':topic,'why_it_matters':'待分析：请结合客户需求、竞争和产品组合评估。','strategic_question':'这条变化对北美 Mid-Market 3-Phase UPS 的影响是什么？','url':link}
def analyze(items):
 key=os.getenv('OPENAI_API_KEY')
 if not key or not items:return items
 model=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
 for a in items[:15]:
  prompt={'model':model,'temperature':0.2,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':'你是数据中心电力基础设施行业分析师。仅依据提供的RSS标题和摘要，中文简洁输出JSON对象，字段title_zh,summary_zh,why_it_matters,strategic_question。不要编造事实、数据、时间或暗示读过全文；若信息不足明确说明。面向全球mid-market三相UPS产品负责人，侧重北美市场。每字段不超过110个汉字。'},{'role':'user','content':json.dumps({'title':a['title'],'description':a['summary_zh'],'source':a['source']},ensure_ascii=False)}]}
  try:
   req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=json.dumps(prompt).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
   with urllib.request.urlopen(req,timeout=35) as r:result=json.load(r)
   obj=json.loads(result['choices'][0]['message']['content'])
   for field in ('title_zh','summary_zh','why_it_matters','strategic_question'):
    if isinstance(obj.get(field),str):a[field]=obj[field]
  except Exception as e:print('AI summary failed:',str(e)[:150])
 return items
def main():
 old=json.loads(PATH.read_text()) if PATH.exists() else {'articles':[]}
 existing={a['id']:a for a in old.get('articles',[]) if not a['id'].startswith('demo-')}
 incoming=[]
 for name,url,topic in FEEDS:
  try:
   found=list(parse(get(url),name,topic));incoming.extend(found);print(name,len(found))
  except Exception as e:print('Feed unavailable:',name,str(e)[:140])
 new=[a for a in incoming if a['id'] not in existing]
 new.sort(key=lambda a:a['published'],reverse=True)
 analyze(new)
 for a in new:existing[a['id']]=a
 articles=sorted(existing.values(),key=lambda a:a.get('published',''),reverse=True)[:500]
 if not articles:print('No live items; preserving demo data');return
 payload={'updated_at':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'articles':articles}
 PATH.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
 print('Saved',len(articles),'articles; new',len(new))
if __name__=='__main__':main()
