**URL**
/api/auth/logout

**Header required**
```json
{"Authorization": "Bearer {access_token}"}
```

---
Responses

200
```json
{"detail": "Logged out successfully"}
```

401
```json
{"detail": "Invalid token"}
```

401
```json
{"detail": "Token revoked"}
```

422
```json
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string",
      "input": "string",
      "ctx": {}
    }
  ]
}
```
