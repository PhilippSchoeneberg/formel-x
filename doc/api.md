# API

All endpoints are under `/api` and use JSON. Interactive docs are served at `/api/docs`.

"Owner" means the logged-in account must own the group (`401` when not logged in, `403`
when logged in as someone else). Errors return `{"detail": "<code>"}` (or FastAPI's list
of validation errors for `422`).

## Auth

| Method | Path | Body | Result |
| --- | --- | --- | --- |
| GET | `/auth/me` | | `{"account": {id, email} \| null}` |
| POST | `/auth/register` | `{email, password}` | `201 {"account"}`, `409 account_exists`, `422 password_too_short` (under 8 characters) / `password_too_long`, `429 too_many_attempts` |
| POST | `/auth/login` | `{email, password}` | `{"account"}`, `401 invalid_credentials`, `429 too_many_attempts` |
| POST | `/auth/logout` | | `204` |

Register and login set the session cookie. `429` responses carry a `Retry-After` header in
seconds; see [deployment.md](deployment.md#login-protection) for the limits.

## Groups

| Method | Path | Access | Notes |
| --- | --- | --- | --- |
| GET | `/groups/mine` | logged in | Groups owned by the account, sorted by name |
| GET | `/groups/by-name?name=` | public | `404 group_not_found` |
| POST | `/groups/lookup` | public | Body `{ids: [..]}` → the groups that still exist |
| POST | `/groups` | logged in | Body `{name}`; `409 group_exists` |
| PATCH | `/groups/{id}` | owner | Body `{name}`; `409 group_exists` |
| DELETE | `/groups/{id}` | owner | Deletes the group and all its content |

Group objects: `{id, name, owner_id}`.

## Elements

| Method | Path | Access | Notes |
| --- | --- | --- | --- |
| GET | `/elements` | public | All 118 elements `{symbol, name, system_group, system_period}` |
| GET | `/groups/{id}/elements` | public | Symbols in the group's learning list |
| PUT | `/groups/{id}/elements/{symbol}` | owner | Add (idempotent); `404 element_not_found` |
| DELETE | `/groups/{id}/elements/{symbol}` | owner | Remove |

## Categories

| Method | Path | Access | Notes |
| --- | --- | --- | --- |
| GET | `/groups/{id}/categories?type=compound\|question` | public | `type` optional |
| POST | `/groups/{id}/categories` | owner | Body `{name, type}`; `409 category_exists` (same name and type) |
| PATCH | `/categories/{id}` | owner | Body `{name}` |
| DELETE | `/categories/{id}` | owner | Also deletes its compounds/questions |

Category objects: `{id, name, type, group_id}`.

## Compounds and questions

`{kind}` is `compounds` or `questions`.

| Method | Path | Access | Notes |
| --- | --- | --- | --- |
| GET | `/groups/{id}/{kind}?category_id=&difficulty=` | public | Filters optional |
| POST | `/groups/{id}/{kind}` | owner | `422 invalid_category` if the category isn't in this group or has the other type |
| PATCH | `/{kind}/{entry_id}` | owner | Full body, same as POST |
| DELETE | `/{kind}/{entry_id}` | owner | |

Compound body:

```json
{
  "correct_name": "Water", "wrong_name1": "…", "wrong_name2": "…", "wrong_name3": null, "wrong_name4": null,
  "correct_formula": "H_2O", "wrong_formula1": "…", "wrong_formula2": "…", "wrong_formula3": null, "wrong_formula4": null,
  "difficulty": "easy", "category_id": 1
}
```

Question body:

```json
{
  "question": "…", "correct_answer": "…", "wrong_answer1": "…", "wrong_answer2": "…",
  "wrong_answer3": null, "wrong_answer4": null, "difficulty": "medium", "category_id": 2
}
```

Text is trimmed; empty optional answers become `null`. Formulas use the notation `H_2O`,
`SO_4^{2-}` and are rendered by the frontend.
