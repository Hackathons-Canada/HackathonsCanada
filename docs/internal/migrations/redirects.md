# Resolving `django.db.migrations.exceptions.InconsistentMigrationHistory` Error

If you encounter the error
`django.db.migrations.exceptions.InconsistentMigrationHistory: Migration socialaccount.0001_initial is applied before its dependency sites.0001_initial on database 'default'.`
while migrating, follow these steps to resolve it:

---

## Steps to Resolve

### 1. Comment Out Apps and Middleware

Open the **settings file** (`common.py`) and temporarily comment out the following configurations:

In the `INSTALLED_APPS` section, comment out:

```python
'django.contrib.sites',
'django.contrib.redirects',
```

In the `MIDDLEWARE` section, comment out:

```python
'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
```

After updating the settings, save the file.

---

### 2. Roll Back the Problematic Migrations

Run the following Django command in your terminal to roll back the `socialaccount` app's migrations to the start (zero):

```bash
python manage.py migrate socialaccount zero
```

This will unapply all migrations related to the `socialaccount` app.

---

### 3. Restore Settings

After rolling back the migrations, revert the changes you made in `common.py`:

1. Uncomment `'django.contrib.sites'` and `'django.contrib.redirects'` in the `INSTALLED_APPS` section.
2. Uncomment `'django.contrib.redirects.middleware.RedirectFallbackMiddleware'` in the `MIDDLEWARE` section.

Save the file.

---

### 4. Reapply Migrations

Re-run the migrations step-by-step:

```bash
python manage.py migrate
```

This will reapply all migrations in the correct order, resolving the inconsistent migration history.

---

### Summary of Commands

Here’s a quick list of the commands you’ll need:

```bash
# Step 2: Roll back socialaccount migrations
python manage.py migrate socialaccount zero

# Step 4: Reapply migrations
python manage.py migrate
```
