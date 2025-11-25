from fastapi import APIRouter
from models import AnalyticsResponse


def init_admin_routes(admin_agent):
    """Initialize admin routes with dependencies"""

    router = APIRouter(prefix="/api/admin", tags=["Admin"])

    @router.get("/analytics", response_model=AnalyticsResponse)
    def get_analytics():
        """Get comprehensive analytics (admin only)"""
        analytics = admin_agent.generate_analytics()
        return AnalyticsResponse(**analytics)

    @router.get("/trends")
    def get_order_trends(days: int = 7):
        """Get order trends analysis"""
        trends = admin_agent.get_order_trends(days)
        return trends

    @router.get("/issues")
    def get_system_issues():
        """Identify potential operational issues"""
        issues = admin_agent.identify_issues()
        return {"issues": issues}

    return router
