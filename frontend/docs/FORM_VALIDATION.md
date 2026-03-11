# Form Validation Matrix

## Shared behavior

- `frontend/src/formSupport.js` is the shared frontend layer for:
  normalization (`normalizeUsernameValue`, `normalizeOptionalTextValue`, `normalizeMultilineTextValue`);
  server error extraction (`resolveFormApiError`);
  double-submit protection (`useSubmitLock`).
- Backend field errors are mapped from `ApiError.fieldErrors`.
- Form-level messages use the same pattern everywhere: field errors stay under inputs, generic/server errors stay in the form banner.

## Active runtime forms

| Form | Frontend validation | Normalization | Submit guard |
|---|---|---|---|
| Login | `username` required, regex `^[a-zA-Z0-9_.-]{4,64}$`; `password` required | username trimmed + lowercased | `useSubmitLock` |
| Patient registration | `first_name` required, `last_name` required, username regex, strong password, confirm password match | names trimmed and whitespace-collapsed, username trimmed + lowercased | `useSubmitLock` |
| Create question | `text` required, `10..4000` chars | multiline text trimmed line-by-line | `useSubmitLock` |
| Answer question | `text` required, `2..2000` chars; role must be `doctor`; doctor must be verified | multiline text trimmed line-by-line | per-question submit lock + disabled button |
| Profile update | at least one of `first_name/last_name`; each field max `120` | names trimmed and whitespace-collapsed | `useSubmitLock` |
| Change password | current password required; new password strong; new password must differ from current; confirmation must match | none beyond native input value | `useSubmitLock` |
| Doctor document upload | at least one file; max `10` files; extensions `pdf/png/jpg/jpeg/webp`; max `8 MB` per file | file list normalized by browser file input | `useSubmitLock` |

## Planned doctor registration form

Doctor self-registration is still postponed in the public runtime, but the frontend validation contract is now fixed for the future native form:

| Step | Required validation |
|---|---|
| Identity | `username` required + normalized with the same rule as login/register; strong password; optional trimmed `first_name` and `last_name` |
| Specializations | `specialization_ids` must contain at least one positive id and no duplicates |
| Documents | at least one file, same file constraints as doctor document upload, multipart `FormData` |

## Server error strategy

- `401`: auth/session problems are shown as form-level messages or route-level redirects.
- `403`: role or verification errors are shown as form-level messages before or after the API round-trip.
- `409`: conflict cases such as duplicate `username` are converted into human-readable form banners.
- `422`: backend validation issues are mapped to field-level errors through `ApiError.fieldErrors`.

## Input normalization policy

- Usernames are always lowercased and stripped before submission.
- Person names are trimmed and internal repeated spaces are collapsed.
- Question/reply text keeps line breaks, but trailing whitespace and empty outer lines are trimmed.
