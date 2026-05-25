"""
CNKI 配置常量。

所有选择器、URL 模式、搜索/排序类型映射集中管理于此。
CNKI 前端变更时只需修改此文件。

最后 CNKI 前端验证日期: 2025-05-25
"""

# ============ URL ============

CNKI_HOME_URL = "https://www.cnki.net/"
CNKI_NAVI_URL = "https://navi.cnki.net/knavi/"
CNKI_KNS_PREFIX = "https://kns.cnki.net/"

# ============ 搜索类型映射 ============

SEARCH_TYPES: dict[str, str] = {
    "主题": "SU",
    "篇关摘": "TKA",
    "关键词": "KY",
    "篇名": "TI",
    "全文": "FT",
    "作者": "AU",
    "第一作者": "FI",
    "通讯作者": "RP",
    "作者单位": "AF",
    "基金": "FU",
    "摘要": "AB",
    "参考文献": "RF",
    "分类号": "CLC",
    "文献来源": "LY",
    "DOI": "DOI",
}

SEARCH_TYPE_VALUES: dict[str, str] = {
    "主题": "SU$%=|",
    "篇关摘": "TKA$%=|",
    "关键词": "KY$=|",
    "篇名": "TI$%=|",
    "全文": "FT$%=|",
    "作者": "AU$=|",
    "第一作者": "FI$=|",
    "通讯作者": "RP$%=|",
    "作者单位": "AF$%",
    "基金": "FU$%|",
    "摘要": "AB$%=|",
    "参考文献": "RF$%=|",
    "分类号": "CLC$=|??",
    "文献来源": "LY$%=|",
    "DOI": "DOI$=|?",
}

SEARCH_TYPE_ALIASES: dict[str, str] = {
    "subject": "主题",
    "theme": "主题",
    "keyword": "关键词",
    "keywords": "关键词",
    "title": "篇名",
    "author": "作者",
    "first_author": "第一作者",
    "corresponding_author": "通讯作者",
    "affiliation": "作者单位",
    "institution": "作者单位",
    "fund": "基金",
    "abstract": "摘要",
    "fulltext": "全文",
    "reference": "参考文献",
    "source": "文献来源",
    "doi": "DOI",
}

# ============ 排序类型映射 ============

SORT_TYPES: dict[str, str] = {
    "相关度": "FFD",
    "发表时间": "PT",
    "被引": "CF",
    "下载": "DFR",
    "综合": "ZH",
}

SORT_TYPE_ALIASES: dict[str, str] = {
    "relevance": "相关度",
    "date": "发表时间",
    "publish_time": "发表时间",
    "time": "发表时间",
    "cited": "被引",
    "citation": "被引",
    "citations": "被引",
    "download": "下载",
    "downloads": "下载",
    "composite": "综合",
    "general": "综合",
}

# ============ 引文格式 ============

CITATION_STYLES = ["gbt7714", "apa", "mla", "chicago", "vancouver"]

# ============ 导出格式 ============

EXPORT_FORMATS = ["csv", "json", "bibtex", "ris"]

# ============ Playwright 配置 ============

BROWSER_TIMEOUT = 30_000  # 30秒总超时 (ms)
NAVIGATION_TIMEOUT = 60_000  # 60秒导航超时 (ms)
IDLE_TIMEOUT = 600  # 10分钟空闲关闭 (秒)
HUMAN_TYPING_DELAY = (0.02, 0.06)  # 字符输入间隔范围 (秒)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
]

# ============ 选择器（CNKI 2025-05-25 验证） ============

# 首页搜索框
SELECTOR_SEARCH_INPUT = "#txt_SearchText"
# 搜索按钮
SELECTOR_SEARCH_BTN = ".search-btn"
# 搜索类型下拉框
SELECTOR_SEARCH_TYPE_DROPDOWN = "#DBFieldBox"
# 搜索类型选项列表
SELECTOR_SEARCH_TYPE_LIST = "#DBFieldList"
# 搜索类型选项模板 → f'a[value="{value}"]'
# 结果表格行
SELECTOR_RESULT_ROWS = 'table.result-table-list tbody tr'
# 结果标题链接
SELECTOR_TITLE_LINK = 'a.fz14'
# 结果作者
SELECTOR_AUTHORS = 'td.author a'
# 结果来源
SELECTOR_SOURCE = 'td.source a'
# 结果日期
SELECTOR_DATE = 'td.date'
# 结果被引
SELECTOR_CITED = 'td.quote a'
# 结果下载
SELECTOR_DOWNLOAD = 'td.download a'
# 翻页按钮
SELECTOR_NEXT_PAGE = "#PageNext"

# 详情页
SELECTOR_DETAIL_TITLE = '.wx-tit h1'
SELECTOR_DETAIL_TITLE_EN = '.wx-tit h2'
SELECTOR_DETAIL_AUTHORS = 'h3.author span a'
SELECTOR_DETAIL_INSTITUTIONS = 'h3.orgn span a'
SELECTOR_DETAIL_ABSTRACT = '#ChDivSummary'
SELECTOR_DETAIL_ABSTRACT_EN = '#EnChDivSummary'
SELECTOR_DETAIL_KEYWORDS = 'p.keywords a'
SELECTOR_DETAIL_SOURCE = 'div.top-tip a[href*="navi.cnki.net"]'
SELECTOR_DETAIL_INFO = 'div.top-tip span'
SELECTOR_DETAIL_DOI = 'li.top-space p'
SELECTOR_DETAIL_CITED = 'span#refs a, div.total-inform span:has-text("被引") + em'
SELECTOR_DETAIL_DOWNLOAD = 'span#DownLoadParts a, div.total-inform span:has-text("下载") + em'
SELECTOR_DETAIL_FUND = 'li:has-text("基金") p, p.funds span'
SELECTOR_DETAIL_CLASSIFICATION = 'li:has-text("分类号") p'

# 弹窗/遮罩选择器列表
POPUP_SELECTORS: list[tuple[str, str]] = [
    ("#close", "css"),
    (".close", "css"),
    ('//div[contains(@class,"popup")]//a[contains(text(),"关闭")]', "xpath"),
    ('//div[contains(@class,"modal")]//button[contains(text(),"关闭")]', "xpath"),
    ('//div[contains(@class,"layui-layer")]//a[contains(@class,"layui-layer-close")]', "xpath"),
]
