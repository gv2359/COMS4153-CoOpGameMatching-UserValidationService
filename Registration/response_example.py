steam_validate_responses = {
    200: {
        "description": "Steam user found successfully.",
        "content": {
            "application/json": {
                "example": {
                    "statusCode": 200,
                    "message": "Steam user found successfully.",
                    "steam_details": {
                        "steamid": "76561197960287930",
                        "personaname": "GabeN",
                        "profileurl": "https://steamcommunity.com/id/gaben",
                        "avatar": "https://example.com/avatar.jpg",
                        "avatarmedium": "https://example.com/avatarmedium.jpg",
                        "avatarfull": "https://example.com/avatarfull.jpg",
                    }
                }
            }
        }
    },
    401: {
        "description": "Unauthorized - Steam API key issue.",
        "content": {
            "application/json": {
                "example": {
                    "statusCode": 401,
                    "message": "Unauthorized - Invalid API key",
                }
            }
        }
    },
    404: {
        "description": "User doesn't exist on Steam.",
        "content": {
            "application/json": {
                "example": {
                    "statusCode": 404,
                    "message": "User doesn't exist on Steam"
                }
            }
        }
    },
    500: {
        "description": "Internal server error contacting Steam API.",
        "content": {
            "application/json": {
                "example": {
                    "statusCode": 500,
                    "message": "Error contacting Steam API"
                }
            }
        }
    },
    422: {
        "description": "Validation Error - Invalid or missing query parameter.",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["query", "steam_id"],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                }
            }
        }
    }
}