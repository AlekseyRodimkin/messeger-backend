**URL**
/api/auth/register

**Body required**
```json
{"refresh_token": "string"}
```
---
Responses

200
```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```

401
```json
{"detail": "Token revoked"}
```


401
```json
{"detail": "User not found"}
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
