
## Endpoints d'Authentification

### User Registration (UserRegistrationView)

Permet à un utilisateur de s'inscrire avec son email, prénom, et nom.

- **URL** : `/api/register/`
- **Méthode** : `POST`
- **Paramètres** :
- `email` (string) : email de l'utilisateur
- `password` (string) : mot de passe
- `first_name` (string, optionnel) : prénom de l'utilisateur
- `last_name` (string, optionnel) : nom de l'utilisateur

### Email Validation Request (EmailValidateRequestView)

Permet à un utilisateur de demander la validation de son adresse email.

- **URL** : `/api/request-email-validation/`
- **Méthode** : `POST`
- **Paramètres** :
- `email` (string) : email de l'utilisateur

### Account Activation (ActivateAccountView)

Permet à un utilisateur d'activer son compte après avoir reçu un OTP par email.

- **URL** : `/api/activate/`
- **Méthodes** :
- `GET` : activation à partir des paramètres d'URL (otp et email)
- `POST` : activation à partir des données JSON (email et otp)

### Login (LoginView)

Permet à un utilisateur de se connecter avec son email et mot de passe.

- **URL** : `/api/login/`
- **Méthode** : `POST`
- **Paramètres** :
- `email` (string) : email de l'utilisateur
- `password` (string) : mot de passe

### Google Login (GoogleLoginView)

Permet à un utilisateur de se connecter via Google OAuth en utilisant un code d'autorisation.

- **URL** : `/api/google-login/`
- **Méthode** : `POST`
- **Paramètres** :
- `code` (string) : code d'autorisation Google

### Password Change (ChangePasswordView)

Permet à un utilisateur de changer son mot de passe.

- **URL** : `/api/change-password/`
- **Méthode** : `POST`
- **Paramètres** :
- `old_password` (string) : ancien mot de passe de l'utilisateur
- `new_password` (string) : nouveau mot de passe

### Set Password (SetPasswordView)

Permet à un utilisateur de définir un nouveau mot de passe après avoir reçu un lien de réinitialisation par email.

- **URL** : `/api/set-password/`
- **Méthode** : `POST`
- **Paramètres** :
- `email` (string) : email de l'utilisateur
- `password` (string) : nouveau mot de passe

### Password Reset Request (PasswordResetRequestView)

Permet à un utilisateur de demander la réinitialisation de son mot de passe par email.

- **URL** : `/api/request-password-reset/`
- **Méthode** : `POST`
- **Paramètres** :
- `email` (string) : email de l'utilisateur

### Password Reset Confirm (PasswordResetConfirmView)

Permet à un utilisateur de confirmer la réinitialisation de son mot de passe après avoir reçu un lien de réinitialisation par email.

- **URL** : `/api/confirm-password-reset/`
- **Méthode** : `POST`
- **Paramètres** :
- `email` (string) : email de l'utilisateur
- `token` (string) : token de réinitialisation

## Exemples d'Utilisation

Voici comment utiliser ces endpoints avec curl :

```bash
# Exemple d'inscription
curl -X POST http://localhost:8000/api/register/ -d "email=user@example.com&password=securepassword"

# Exemple de connexion
curl -X POST http://localhost:8000/api/login/ -d "email=user@example.com&password=securepassword"

# Exemple de demande de réinitialisation de mot de passe
curl -X POST http://localhost:8000/api/request-password-reset/ -d "email=user@example.com"
