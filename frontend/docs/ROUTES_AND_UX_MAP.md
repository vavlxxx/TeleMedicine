# Routes And UX Map

## Canonical routes

| Route | Access | Screen | Notes |
|---|---|---|---|
| `/` | public | landing | discovery entrypoint, links to doctors/questions/auth |
| `/login-desktop-ru` | guest | login | accepts `returnTo`, `registered`, `logged_out` |
| `/registration-desktop-ru` | guest | patient registration | preserves `returnTo` for the next login |
| `/doctor-directory-with-filters-ru` | public | doctor directory | supports `specialization_id` |
| `/doctor-public-profile-ru` | public | doctor profile | supports `doctor_id` |
| `/public-questions-feed-ru` | public | Q&A feed | supports `question_id` |
| `/account` | protected | current user profile | default authenticated destination for `patient` and `doctor` |
| `/admin-doctor-moderation` | protected `admin/superuser` | admin moderation | default authenticated destination for `admin` and `superuser` |
| `/404` | public | fallback page | explicit not-found route |

## Semantic aliases

| Alias | Redirect target | Access |
|---|---|---|
| `/login` | `/login-desktop-ru` | guest |
| `/register` | `/registration-desktop-ru` | guest |
| `/doctors` | `/doctor-directory-with-filters-ru` | public |
| `/questions` | `/public-questions-feed-ru` | public |
| `/profile` | `/account` | protected |
| `/admin` | `/admin-doctor-moderation` | protected `admin/superuser` |

## Redirect rules

- Unknown path renders the not-found page instead of silently falling back to landing.
- Guest-only pages redirect authenticated users to their default destination:
  `patient/doctor -> /account`, `admin/superuser -> /admin-doctor-moderation`.
- Protected pages redirect anonymous users to `/login-desktop-ru?returnTo=<original-path>`.
- Login redirects to `returnTo` when it is a safe in-app path; otherwise it uses the role-based default destination.
- Registration redirects to login with `?registered=1` and preserves `returnTo`.
- Logout redirects to `/login-desktop-ru?logged_out=1`.
- Role mismatch on a protected route redirects to `/account?access=denied` or the default authenticated route for the current role.

## Screen-to-screen flow

- Landing -> doctors, questions, login/register, profile/admin.
- Login -> profile/admin after success, register, landing.
- Registration -> login, landing.
- Doctor directory -> doctor profile, questions, landing.
- Doctor profile -> directory, questions.
- Questions -> login/register with `returnTo`, doctor directory, landing.
- Account -> landing, doctors, questions, admin moderation for admin roles, logout.
- Admin moderation -> account, landing.

## UX guard matrix

| Scenario | Behavior |
|---|---|
| Anonymous user opens `/account` | redirect to login with `returnTo` |
| Patient opens `/admin` | redirect to `/account?access=denied` |
| Non-doctor tries doctor-only answer action | inline error before API request |
| Unverified doctor tries answer action | inline error before API request |
| Non-doctor tries doctor document upload | inline error before API request |
