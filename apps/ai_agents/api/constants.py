"""
Constants used across the AI Agents API.
"""

# Review constants
REVIEW_ORDERING_FIELDS = ['created_at', 'rating', '-created_at', '-rating']

# Review field constraints
REVIEW_CONSTRAINTS = {
    'rating': {
        'min': 1,
        'max': 5
    },
    'headline': {
        'max_length': 200
    },
    'review_text': {
        'max_length': 2000
    },
    'short_feedback': {
        'max_length': 200
    }
}

# API Documentation
REVIEW_API_ENDPOINTS = {
    "agent_reviews": {
        "list": {
            "path": "/agents/{ai_agent_pk}/reviews/",
            "method": "GET",
            "description": "List all reviews for an AI Agent",
            "query_params": {
                "ordering": "Sort by: created_at, rating, -created_at, -rating",
                "search": "Search in headline and review_text"
            }
        },
        "create": {
            "path": "/agents/{ai_agent_pk}/reviews/",
            "method": "POST",
            "description": "Create a new review for an AI Agent instance"
        },
        "retrieve": {
            "path": "/agents/{ai_agent_pk}/reviews/{pk}/",
            "method": "GET",
            "description": "Get details of a specific review"
        },
        "stats": {
            "path": "/agents/{ai_agent_pk}/reviews/stats/",
            "method": "GET",
            "description": "Get review statistics for an AI Agent"
        }
    },
    "execution_reviews": {
        "list": {
            "path": "/agents/{ai_agent_pk}/execution-reviews/",
            "method": "GET",
            "description": "List all execution reviews for an AI Agent",
            "query_params": {
                "ordering": "Sort by: created_at, rating, -created_at, -rating",
                "search": "Search in short_feedback"
            }
        },
        "create": {
            "path": "/agents/{ai_agent_pk}/execution-reviews/",
            "method": "POST",
            "description": "Create a new execution review"
        },
        "retrieve": {
            "path": "/agents/{ai_agent_pk}/execution-reviews/{pk}/",
            "method": "GET",
            "description": "Get details of a specific execution review"
        }
    }
} 