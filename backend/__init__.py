"""Python backend package for A. Sai Kali Chakravarthi's portfolio platform.

Provides domain models, portfolio data repositories, academic and technical
analytics engines, contact processing pipelines, and framework-agnostic HTTP
routing compatible with both Vercel Python Serverless Functions and local HTTP
servers.
"""

from backend.router import dispatch_request

__all__ = ["dispatch_request"]
__version__ = "1.0.0"
