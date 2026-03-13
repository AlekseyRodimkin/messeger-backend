**URL**
/api/auth/register

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
{"detail": "ok"}
```

400
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
