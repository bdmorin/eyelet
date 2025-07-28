"""Domain-specific exceptions"""


class RiggingError(Exception):
    """Base exception for all Rigging errors"""
    pass


class HookConfigurationError(RiggingError):
    """Error in hook configuration"""
    pass


class HookExecutionError(RiggingError):
    """Error during hook execution"""
    pass


class WorkflowError(RiggingError):
    """Error in workflow execution"""
    pass


class TemplateError(RiggingError):
    """Error in template processing"""
    pass


class DiscoveryError(RiggingError):
    """Error in hook/tool discovery"""
    pass