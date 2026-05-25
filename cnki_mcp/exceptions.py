"""CNKI MCP 自定义异常层级"""


class CNKIError(Exception):
    """CNKI 服务基础异常"""
    pass


class BrowserError(CNKIError):
    """浏览器启动/导航失败"""
    pass


class SearchError(CNKIError):
    """搜索无结果/搜索失败"""
    pass


class DetailError(CNKIError):
    """论文详情解析失败"""
    pass


class ValidationError(CNKIError):
    """参数校验失败"""
    pass


class CitationError(CNKIError):
    """引文格式化失败"""
    pass


class ExportError(CNKIError):
    """导出失败"""
    pass
