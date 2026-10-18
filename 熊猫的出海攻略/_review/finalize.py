import pathlib,json,re,datetime,urllib.parse,zipfile
p=pathlib.Path(__file__).resolve().parent.parent
ledger=json.loads((p/'_review/text-review.json').read_text());rows=json.loads((p/'summary.json').read_text());rows.sort(key=lambda r:r['homepageIndex'])
assert len(rows)==100 and len({r['url'] for r in rows})==100
prepared=[]
for r in rows:
 text=(p/r['file']).read_text()
 for old,new in ledger['corrections'].get(str(r['homepageIndex']),{}).items():
  pattern=r'(?<![A-Za-z])'+re.escape(old)+r'(?![A-Za-z])' if re.fullmatch('[A-Za-z]+',old) else re.escape(old)
  text,n=re.subn(pattern,lambda m:new,text)
  if not n:raise ValueError(f'Correction not found: index {r["homepageIndex"]} {old}')
 prepared.append((r,text))
now=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
for r,text in prepared:
 k=str(r['homepageIndex']);unresolved=k in ledger['needs_review'] and k not in ledger['resolved']
 r.update(status='needs_review' if unresolved else 'ok',review_status='needs_review' if unresolved else 'verified',reviewed_at=now,review_scope=ledger['scope'])
 if k in ledger['needs_review']:r['review_note']=ledger['needs_review'][k]
 if k in ledger['resolved']:r['review_evidence']=['_review/'+f for f in ledger['resolved'][k]];r['review_note']='已核对画面并修订；'+ledger.get('source_notes',{}).get(k,'')
 if k in ['19','34']:r['extraction_method']='speech_recognition';r['supplementary_extraction_method']='screen_text'
 if k=='0':r['access_restriction']='paid_content';r['content_scope']='public_preview_only'
 (p/r['file']).write_text(text)
 rawp=p/r['raw_file'];raw=json.loads(rawp.read_text());raw['review_status']=r['review_status'];raw['reviewed_at']=now;raw['review_scope']=ledger['scope'];raw['extraction_method']=r['extraction_method'];raw['review_note']=r.get('review_note','标题、开头、主题与长度核对通过。')
 if k=='0':raw['access_restriction']='paid_content';raw['content_scope']='public_preview_only'
 if k in ledger['resolved']:raw['review_evidence']=r['review_evidence']
 rawp.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
(p/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
def label(s):return re.sub(r'[\r\n]+',' ',s).replace('|','\\|').replace('[','\\[').replace(']','\\]')
idx=['# 熊猫的出海攻略：前100条视频文案','','按本次主页视觉顺序，包含置顶，跳过图文；序号从0开始。第一条为付费视频，仅含公开试看文案。','','[复核记录](提取说明与复核记录.md) · [合并阅读](前100条文案汇编.md)','','| 序号 | 视频链接 | 标题 | 写入时间 |','| --- | --- | --- | --- |']
for r in rows:
 title=r['title'].split('\n')[0];title=('【仅公开试看】' if r['homepageIndex']==0 else '')+title
 idx.append(f"| {r['homepageIndex']} | {r['url']} | [{label(title)}]({urllib.parse.quote(r['file'])}) | {r['writtenAt']} |")
(p/'index.md').write_text('\n'.join(idx)+'\n')
full=['# 熊猫的出海攻略：前100条文案汇编','','按主页顺序提取，包含置顶，跳过图文。第1条仅公开试看部分；其余文案经正文检查，异常位置已结合画面复核。原始ASR保存在transcripts中，未对作者事实主张作独立核实。','']
for r in rows:
 full+=['## '+str(r['homepageIndex']+1)+'. '+r['title'].split('\n')[0], '']
 if r['homepageIndex']==0:full+=['> 仅公开试看部分，后续内容显示“购买后可看”。','']
 full += [(p/r['file']).read_text().strip(),'']
(p/'前100条文案汇编.md').write_text('\n'.join(full)+'\n')
ok=sum(r['status']=='ok' for r in rows);pending=100-ok
report=['# 提取说明与复核记录','','- 作者：熊猫的出海攻略（PandaChuhai）。','- 范围：本次主页前100条视频，按视觉顺序，含置顶，跳过图文。',f'- 产出：100个不同视频ID，100份文案；{ok}条内容检查通过，{pending}条受限或待复核。','- 第0条：付费视频，40秒画面明确提示“购买后可看 / 购买完整版（390钻）”；仅保留公开试看文案，不计为完整提取。','- 复核范围：逐条阅读正文，核对标题、开头、主题、长度；对异常条目查看字幕和文字卡片。不是全部逐字听校，也不独立验证作者所述事实、数据或投资观点。','- 转写：默认URL路径因yt-dlp要求fresh cookies而失败，100条均自动回退至browser-memory / qwen3-asr-flash；不保存音视频文件或媒体直链。','- 原始ASR文本保留；修订仅应用于Markdown文案，画面依据保存在_review。','','## 画面复核明细','','| 主页序号 | 结果 | 核对内容 |','| --- | --- | --- |']
for k,note in ledger['needs_review'].items():
 i=int(k);result='仅公开试看' if i==0 else ('已核对' if k in ledger['resolved'] else '待复核')
 report.append(f'| {i} | {result} | {label(note)} |')
report += ['','原视频第59条存在“也不是不能开投资户 / 目前不支持开投资账户”的表述矛盾，两处字幕都可见，已忠实保留，未代作者改写。','','## 本次流程修正','','- 技能补充付费试看识别与交付规则。','- 修复多行标题破坏索引表格的问题，新增回归测试。25项Node测试、12项Python测试及npm run check通过。','- 抽帧遇到部分定位超时，后续通过定点截图补查；仅对实际可辨认内容作修订。']
(p/'提取说明与复核记录.md').write_text('\n'.join(report)+'\n')
archive=p/'熊猫的出海攻略_前100条文案.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in [p/r['file'] for r in rows]+[p/x for x in ['index.md','summary.json','video_urls.json','account.json','前100条文案汇编.md','提取说明与复核记录.md']]+[p/r['raw_file'] for r in rows]:z.write(f,f.relative_to(p))
print(json.dumps({'files':100,'unique_ids':100,'verified':ok,'needs_review':pending,'archive_bytes':archive.stat().st_size,'markdown_chars':sum(len(t) for _,t in prepared)},ensure_ascii=False))
