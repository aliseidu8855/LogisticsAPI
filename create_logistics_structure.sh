#!/bin/bash

# --- CONFIGURATION ---
DJANGO_SETTINGS_DIR_NAME="config" # You can change this! (e.g., logistics_project, core)
# --- END CONFIGURATION ---

if [ -f "manage.py" ]; then
  echo "WARNING: 'manage.py' already exists in the current directory: $(pwd)"
  echo "This script is intended to set up a new project structure."
  read -p "Do you want to proceed and potentially overwrite or add to existing files? (yes/N): " proceed
  if [[ "$proceed" != "yes" ]]; then
    echo "Aborted by user."
    exit 1
  fi
fi

echo "--- Setting up Django project in the CURRENT DIRECTORY: $(pwd) ---"
echo "The Django settings/configuration directory will be named: '$DJANGO_SETTINGS_DIR_NAME'"
read -p "Is this correct? (yes/N): " confirm
if [[ "$confirm" != "yes" ]]; then
  echo "Aborted by user. Please edit DJANGO_SETTINGS_DIR_NAME in the script if needed."
  exit 1
fi

echo "Running: django-admin startproject $DJANGO_SETTINGS_DIR_NAME ."
django-admin startproject "$DJANGO_SETTINGS_DIR_NAME" .
if [ $? -ne 0 ]; then
    echo "ERROR: django-admin startproject failed. Is Django installed and in your PATH?"
    exit 1
fi
echo "Django project core created."

if [ ! -d "apps" ]; then
  mkdir apps
  touch apps/__init__.py
  echo "'apps' directory created."
else
  echo "'apps' directory already exists."
fi

create_app_structure() {
  local app_name=$1
  local app_parent_dir="apps"
  local app_path="$app_parent_dir/$app_name"

  echo "Creating structure for app: $app_name at $app_path"

  mkdir -p "$app_path" # Ensure the specific app directory (e.g., apps/users) exists
  if [ $? -ne 0 ]; then
      echo "ERROR: Could not create directory $app_path"
      exit 1
  fi

  python manage.py startapp "$app_name" "$app_path"
  if [ $? -ne 0 ]; then
      echo "ERROR: python manage.py startapp $app_name $app_path failed."
      echo "Attempting manual creation for $app_name (as fallback)..."
      mkdir -p "$app_path/migrations"
      touch "$app_path/__init__.py"
      touch "$app_path/admin.py"
      echo "from django.apps import AppConfig" > "$app_path/apps.py"
      echo "" >> "$app_path/apps.py"
      echo "class $(echo "$app_name" | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')Config(AppConfig):" >> "$app_path/apps.py"
      echo "    default_auto_field = 'django.db.models.BigAutoField'" >> "$app_path/apps.py"
      echo "    name = 'apps.$app_name'" >> "$app_path/apps.py"
      touch "$app_path/models.py"
      touch "$app_path/tests.py"
      touch "$app_path/views.py"
      touch "$app_path/migrations/__init__.py"
  fi

  touch "$app_path/serializers.py"
  touch "$app_path/urls.py"

  if [[ "$app_name" == "users" || "$app_name" == "inventory" || "$app_name" == "notifications" ]]; then
    touch "$app_path/signals.py"
  fi
  if [[ "$app_name" == "users" ]]; then
    touch "$app_path/permissions.py"
  fi
  if [[ "$app_name" == "notifications" || "$app_name" == "audit_logs" ]]; then
    touch "$app_path/services.py"
  fi
  echo "Structure for app $app_name completed."
}

APPS_LIST=("users" "inventory" "containers" "shipments" "deliveries" "notifications" "audit_logs")
for app in "${APPS_LIST[@]}"; do
  create_app_structure "$app"
done

if [ -d "$DJANGO_SETTINGS_DIR_NAME" ]; then
  touch "$DJANGO_SETTINGS_DIR_NAME/celery.py"
  echo "'$DJANGO_SETTINGS_DIR_NAME/celery.py' created."
else
  echo "WARNING: Django settings directory '$DJANGO_SETTINGS_DIR_NAME' not found. Could not create celery.py."
fi

if [ ! -f ".env" ]; then
  touch .env
  echo "'.env' file created."
else
  echo "'.env' file already exists."
fi

echo ""
echo "--- Project structure setup complete in the current directory ---"
echo "Next Steps:"
echo "1. Add your apps to INSTALLED_APPS in '$DJANGO_SETTINGS_DIR_NAME/settings.py'."
echo "   For example, for the 'users' app, add: 'apps.users.apps.UsersConfig'"
echo "2. Configure your '$DJANGO_SETTINGS_DIR_NAME/settings.py' (database, static files, etc.)."
echo "3. Configure your '.env' file with secrets (SECRET_KEY, DATABASE_URL, etc.)."
echo "4. Ensure your 'requirements.txt' is up-to-date and run 'pip install -r requirements.txt' if needed."
echo "5. Initialize git: 'git init', 'git add .', 'git commit -m \"Initial project structure\"'"