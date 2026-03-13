**URL**
/api/auth/login

**Body required**
```json
{
  "username": "string",
  "password": "stringstri"
}
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
{"detail": "Username already registered"}
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
